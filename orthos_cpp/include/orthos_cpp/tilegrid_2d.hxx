#include <vigra/multi_blocking.hxx>
#include <set>
#include <map>
#include <vector>
#include <algorithm>
#include <iterator>

typedef vigra::MultiBlocking<2> Blocking2d;
typedef typename Blocking2d::Shape Shape2d;
typedef typename Blocking2d::Block Block2d;
typedef vigra::TinyVector<float, 2> Float2;

typedef vigra::TinyVector<int64_t, 1> Shape1;
typedef vigra::TinyVector<int64_t, 3> Shape3;
typedef vigra::Box<int64_t, 3> Block3d;
/**
 * @brief      used to get the appeared and 
 *             disappeared block indexes after
 *             a roi update via updateCurrentRoi
 */




class VisibleBlocksManager{

public:
    VisibleBlocksManager(
        const Blocking2d & blocking2d,
        const Shape2d & tilingShape 
    )

    :   blocking2d_(blocking2d),
        currentRoi_(Shape2d(0),Shape2d(0)),
        tilingShape_(tilingShape),
        visibleBlocks_()
    {
    }

    /**
     * @brief      clear the container of all visible block.
     *             Therefore in the next update via updateCurrentRoi
     *             all blocks in the roi (within tilingShape)
     *             are in the appeared list
     */
    void clearVisibleBlocks(){
        visibleBlocks_.clear();
    }   

    /**
     * @brief      update the current roi
     *
     * @param[in]  begin        left upper corner of visible part
     * @param[in]  end          right lower corner of visible part
     * @param      appeared     vector of indexes of the blocks which
     *                          appeared.
     * @param      disappeared  vector of indexes of the blocks which
     *                          disappeared
     *
     * @return     did any block at all changed the visibility
     */
    bool updateCurrentRoi(
        const Float2 & begin, 
        const Float2 & end,
        std::vector<size_t> & appeared,
        std::vector<size_t> & disappeared
    ){
        const auto iblocks = blocking2d_.intersectingBlocks(begin, end);
        std::set<size_t> newVB(iblocks.begin(), iblocks.end());

        std::set<size_t> a,d;
        std::set_difference(newVB.begin(), newVB.end(), 
                            visibleBlocks_.begin(), visibleBlocks_.end(),
                            std::inserter(a, a.end()));
        std::set_difference(visibleBlocks_.begin(), visibleBlocks_.end(), 
                            newVB.begin(), newVB.end(),
                            std::inserter(d, d.end()));
        
        appeared.assign(a.begin(),a.end());
        disappeared.assign(d.begin(),d.end());

        visibleBlocks_ = newVB;

        return !appeared.empty() || !disappeared.empty();
    }

    const std::set<size_t> & visibleBlocks()const{
        return visibleBlocks_;
    }

    /**
     * @brief      return the bounding box of 
     *             the visible blocks within
     *             the currentRoi (wrt the b)
     *
     * @return     { description_of_the_return_value }
     */
    Block2d boundingRect()const{

    }
  
private:
    const Blocking2d & blocking2d_;
    Block2d currentRoi_;
    Shape2d tilingShape_;
    std::set<size_t> visibleBlocks_;
    
};


struct PlaneInfo{
    uint8_t scrollAxis;
    uint8_t viewAxis[2];
};


struct TileInfo{


    bool tileVisible;
    Block2d roi2d;
    Block3d roi3d;
    uint64_t scrollCoordinate;
    uint64_t timeCoordinate;

    TileInfo copy()const{
        return TileInfo(*this);
    }

    bool operator == (const TileInfo & other){
        if(
            other.tileVisible == tileVisible &&
            other.roi2d == roi2d &&
            other.scrollCoordinate == scrollCoordinate &&
            other.timeCoordinate == timeCoordinate
        ){
            return true;
        }
        return false;
    }

    bool operator != (const TileInfo & other){
        if(
            other.tileVisible == tileVisible &&
            other.roi2d == roi2d &&
            other.scrollCoordinate == scrollCoordinate &&
            other.timeCoordinate == timeCoordinate
        ){
            return false;
        }
        return true;
    }
};


class TileGridManager{
public:
    TileGridManager(
        const Blocking2d & blocking2d,
        const Shape2d & tilingShape,
        const size_t scrollAxis,
        const Shape2d & viewAxis
    )
    :   blocking2d_(blocking2d),
        tilingShape_(tilingShape),
        scrollAxis_(scrollAxis),
        viewAxis_(viewAxis),
        visibleBlocksManager_(blocking2d,tilingShape)
    {
        timeCoordinate_ = 0;
        scrollCoordinate_ = 0;
        auto nTiles = tilingShape[0]*tilingShape[1];
        tileInfos_.resize(nTiles);
        for(size_t i=0; i<nTiles; ++i){
            freeTileIndexes_.insert(i);
            tileInfos_[i].tileVisible = false;
        }

    }

    const TileInfo & tileInfo(const size_t ti)const{
        return tileInfos_[ti];
    }

    /**
     * @brief      update the current roi
     *
     * @param[in]  begin        left upper corner of visible part
     * @param[in]  end          right lower corner of visible part
     * @param      appeared     vector of indexes of the blocks which
     *                          appeared.
     * @param      disappeared  vector of indexes of the blocks which
     *                          disappeared
     *
     * @return     did any block at all changed the visibility
     */
    bool updateCurrentRoi(
        const Float2 & begin, 
        const Float2 & end,
        std::vector<size_t> & appeared,
        std::vector<size_t> & disappeared
    ){
        //////////////////////////////////////////////////////////////////////////////
        // check which blocks appeared and which disappeared
        const auto changed = visibleBlocksManager_.updateCurrentRoi(begin, end, appeared,disappeared);
        
        if(changed){

            //////////////////////////////////////////////////////////////////////////////
            // map block indexes to tile indexes
            ///////////////////////////////////////////////////////////////////////////////
            
            // disappear
            for(auto & bi  : disappeared){
                auto iter = blockIndexToTileIndex_.find(bi);
                const auto ti = iter->second;
                blockIndexToTileIndex_.erase(iter);
                usedTileIndexes_.erase(ti);
                freeTileIndexes_.insert(ti);

                auto & tileInfo = tileInfos_[ti];
                tileInfo.tileVisible = false;
                bi = ti;
            }
            // appear
            for(auto & bi: appeared){
                auto ti = *freeTileIndexes_.begin();
                blockIndexToTileIndex_[bi] = ti;
                freeTileIndexes_.erase(ti);
                usedTileIndexes_.insert(ti);

                auto & tileInfo = tileInfos_[ti];
                tileInfo.tileVisible = true;
                tileInfo.scrollCoordinate = scrollCoordinate_;
                tileInfo.timeCoordinate = timeCoordinate_;
                tileInfo.roi2d = blocking2d_.blockBegin()[bi];

                Shape3 begin3d,end3d;
                begin3d[scrollAxis_] = scrollCoordinate_;
                end3d[scrollAxis_] = scrollCoordinate_+1;
                begin3d[viewAxis_[0]] = tileInfo.roi2d.begin()[0];
                begin3d[viewAxis_[1]] = tileInfo.roi2d.begin()[1];
                end3d[viewAxis_[0]] = tileInfo.roi2d.end()[0];
                end3d[viewAxis_[1]] = tileInfo.roi2d.end()[1];

                tileInfo.roi3d = Block3d(begin3d, end3d);
                bi = ti;
            }
        }

    }

    size_t nVisibleTiles()const{
        return usedTileIndexes_.size();
    }

    template<class OUT_ITER>
    void visibleBlocks(OUT_ITER begin, OUT_ITER end)const{
        for(const auto bi : visibleBlocksManager_.visibleBlocks()){
            *begin = bi;
            ++begin;
        }
    }

    template<class OUT_ITER>
    void visibleTiles(OUT_ITER begin, OUT_ITER end)const{
        for(const auto bi : visibleBlocksManager_.visibleBlocks()){
            const auto ti = blockIndexToTileIndex_.find(bi)->second;
            *begin = ti;
            ++begin;
        }
    }



    void updateScrollCoordinate(const uint64_t scrollCoordinate){
        scrollCoordinate_ = scrollCoordinate;
        for(auto bi : visibleBlocksManager_.visibleBlocks()){
            const auto ti = blockIndexToTileIndex_[bi];
            auto & tileInfo  = tileInfos_[ti];
            tileInfo.scrollCoordinate = scrollCoordinate_;

            Shape3 begin3d = tileInfo.roi3d.begin();
            Shape3 end3d = tileInfo.roi3d.end();
            begin3d[scrollAxis_] = scrollCoordinate_;
            end3d[scrollAxis_] = scrollCoordinate_+1;
            tileInfo.roi3d = Block3d(begin3d, end3d);
        }
    }

    void updateTimeCoordinate(const uint64_t timeCoordinate){
        timeCoordinate_ = timeCoordinate;
        for(auto bi : visibleBlocksManager_.visibleBlocks()){
            const auto ti = blockIndexToTileIndex_[bi];
            tileInfos_[ti].timeCoordinate = timeCoordinate_;
        }
    }

private:



    const Blocking2d  blocking2d_;
    Shape2d tilingShape_;
    size_t scrollAxis_;
    Shape2d viewAxis_;
    VisibleBlocksManager visibleBlocksManager_;


    std::set<size_t> usedTileIndexes_;
    std::set<size_t> freeTileIndexes_;
    uint64_t timeCoordinate_;
    uint64_t scrollCoordinate_;

    // infos per tile
    std::vector<TileInfo> tileInfos_;

    // map block to tile index
    std::map<uint64_t,uint64_t> blockIndexToTileIndex_;
};





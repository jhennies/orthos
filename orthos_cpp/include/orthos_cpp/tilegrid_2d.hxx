#include <vigra/multi_blocking.hxx>
#include <set>
#include <map>
#include <vector>
#include <algorithm>
#include <iterator>
#include <cstdint>
#include <stdexcept>
#include <sstream>
#include <limits>
#include <cmath>


typedef vigra::MultiBlocking<2> Blocking2d;
typedef typename Blocking2d::Shape Shape2d;
typedef typename Blocking2d::Block Block2d;
typedef vigra::TinyVector<float, 2> Float2;

typedef vigra::TinyVector<int64_t, 1> Shape1;
typedef vigra::TinyVector<int64_t, 2> Shape2;
typedef vigra::TinyVector<int64_t, 3> Shape3;
typedef vigra::Box<int64_t, 3> Block3d;
/**
 * @brief      used to get the appeared and 
 *             disappeared block indexes after
 *             a roi update via updateCurrentRoi
 */



#define ORTHOS_CHECK_OP(a,op,b,message) \
    if(!  static_cast<bool>( a op b )   ) { \
       std::stringstream s; \
       s << "Inferno Error: "<< message <<"\n";\
       s << "Inferno check :  " << #a <<#op <<#b<< "  failed:\n"; \
       s << #a " = "<<a<<"\n"; \
       s << #b " = "<<b<<"\n"; \
       s << "in file " << __FILE__ << ", line " << __LINE__ << "\n"; \
       throw std::runtime_error(s.str()); \
    }

/** \def INFERNO_CHECK(expression,message)
    \brief macro for runtime checks
    
    \warning The check is done 
        <B> even in Release mode </B> 
        (therefore if NDEBUG <B>is</B> defined)

    \param expression : expression which can evaluate to bool
    \param message : error message (as "my error")

    <b>Usage:</b>
    \code
        int a = 1;
        INFERNO_CHECK_OP(a==1, "this should never fail")
        INFERNO_CHECK_OP(a>=2, "this should fail")
    \endcode
*/
#define ORTHOS_CHECK(expression,message) if(!(expression)) { \
   std::stringstream s; \
   s << message <<"\n";\
   s << "Inferno assertion " << #expression \
   << " failed in file " << __FILE__ \
   << ", line " << __LINE__ << std::endl; \
   throw std::runtime_error(s.str()); \
 }












class VisibleBlocksManager{

public:
    VisibleBlocksManager(
        const Blocking2d & blocking2d,
        const Shape2d & tilingShape 
    )
    :   blocking2d_(blocking2d),
        currentRoi_(Shape2d(0),Shape2d(0)),
        tilingShape_(tilingShape),
        hasTilingShape_(true),
        visibleBlocks_()
    {
    }

    VisibleBlocksManager(
        const Blocking2d & blocking2d
    )
    :   blocking2d_(blocking2d),
        currentRoi_(Shape2d(0),Shape2d(0)),
        tilingShape_(0),
        hasTilingShape_(false),
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

    std::vector<size_t> intersectingBlocks(
        const Shape2 & begin, 
        const Shape2 & end
    ){

        std::vector<size_t>  iBlocks;
        const Block2d testBlock(begin, end);

        if(hasTilingShape_){
            Shape2 bbegin = begin/blocking2d_.blockShape();
            

            vigra::MultiCoordinateIterator<2> iter(tilingShape_);
            vigra::MultiCoordinateIterator<2> endIter(iter.getEndIterator());

            for(; iter!=endIter; ++iter){
                const Shape2 coord(*iter);
                const Shape2 blockCoord = coord + bbegin;
                const Block2d block =  blocking2d_.blockDescToBlock(blockCoord);
                if(testBlock.intersects(block)){
                    int bi = blockCoord[0] + blockCoord[1]*blocking2d_.blocksPerAxis()[0];
                    iBlocks.push_back(bi);
                }
            }
        }
        else{
            int bi = 0 ;
            for(auto blockIter = blocking2d_.blockBegin(); blockIter!=blocking2d_.blockEnd(); ++blockIter){
                auto  block =*blockIter;
                if(testBlock.intersects(block)){
                    iBlocks.push_back(bi);
                }
                ++bi;
            }
        }
        return std::move(iBlocks);
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

        //const auto iblocks = blocking2d_.intersectingBlocks(begin, end);
        const auto iblocks = intersectingBlocks(begin, end);
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
    bool hasTilingShape_;
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



template<class C, class KEY>
bool hasKey(const C & c, const KEY & key){
    return c.find(key)!=c.end();
}

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
        ORTHOS_CHECK_OP(ti,<,tileInfos_.size(),"");
        return tileInfos_[ti];
    }

    /**
     * @brief      update the current rofreeTileIndexes_i
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
                ORTHOS_CHECK(iter!=blockIndexToTileIndex_.end(),"");
                const auto ti = iter->second;
                blockIndexToTileIndex_.erase(iter);

                ORTHOS_CHECK(hasKey(usedTileIndexes_,ti),"");
                usedTileIndexes_.erase(ti);
                ORTHOS_CHECK(!hasKey(freeTileIndexes_,ti),"");
                freeTileIndexes_.insert(ti);

                auto & tileInfo = tileInfos_[ti];
                tileInfo.tileVisible = false;
                bi = ti;
            }
            // appear
            for(auto & bi: appeared){
                ORTHOS_CHECK_OP(freeTileIndexes_.size(),>,0,"");
                auto ti = *freeTileIndexes_.begin();


                //std::cout<<"ti "<<ti<<"\n";
                //for(auto inSet : freeTileIndexes_){
                //    std::cout<<"   ti "<<inSet<<"\n";
                //}

                ORTHOS_CHECK(hasKey(freeTileIndexes_,ti),"");
                freeTileIndexes_.erase(ti);

                ORTHOS_CHECK(!hasKey(usedTileIndexes_,ti),"");
                usedTileIndexes_.insert(ti);

                ORTHOS_CHECK(blockIndexToTileIndex_.find(bi)==blockIndexToTileIndex_.end(),"");
                blockIndexToTileIndex_[bi] = ti;

      

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


    std::vector<size_t> 
    visibleBlocksInRoi(
        Shape2d roiBegin,
        Shape2d roiEnd
    )const{
        std::vector<size_t> visibleBlocks;
        const Block2d testBlock(roiBegin, roiEnd);
        for(const auto bi : visibleBlocksManager_.visibleBlocks()){
            const auto block = blocking2d_.blockBegin()[bi];
            if(testBlock.intersects(block)){
                visibleBlocks.push_back(bi);
            }
        }
        return std::move(visibleBlocks);
    }

    std::vector<size_t> 
    visibleTilesInRoi2D(
        Shape2d roiBegin,
        Shape2d roiEnd
    )const{
        std::vector<size_t> visibleTiles;
        const Block2d testBlock(roiBegin, roiEnd);
        for(const auto bi : visibleBlocksManager_.visibleBlocks()){
            const auto block = blocking2d_.blockBegin()[bi];
            if(testBlock.intersects(block)){
                const auto ti = blockIndexToTileIndex_.find(bi)->second;
                visibleTiles.push_back(ti);
            }
        }
        return std::move(visibleTiles);
    }


    std::vector<size_t> 
    visibleTilesInRoi3D(
        Shape3 roiBegin,
        Shape3 roiEnd
    )const{
       if(roiBegin[scrollAxis_]<= scrollCoordinate_ && scrollCoordinate_<roiEnd[scrollAxis_]){
            const Shape2d roiBegin2D(roiBegin[viewAxis_[0]], roiBegin[viewAxis_[1]]);
            const Shape2d roiEnd2D(roiEnd[viewAxis_[0]], roiEnd[viewAxis_[1]]);
            return visibleTilesInRoi2D(roiBegin2D, roiEnd2D);
       }
       else{
            std::vector<size_t> res;
            return std::move(res);
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




class StaticTileGridManager{
public:
    StaticTileGridManager(
        const Blocking2d & blocking2d,
        const size_t scrollAxis,
        const Shape2d & viewAxis
    )
    :   blocking2d_(blocking2d),
        scrollAxis_(scrollAxis),
        viewAxis_(viewAxis),
        visibleBlocksManager_(blocking2d),
        timeCoordinate_(),
        scrollCoordinate_(),
        tileInfos_(blocking2d_.numBlocks())
    {
    }
    const TileInfo & tileInfo(const size_t ti)const{
        ORTHOS_CHECK_OP(ti,<,tileInfos_.size(),"");
        return tileInfos_[ti];
    }
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
            for(const auto  ti  : disappeared){
                auto & tileInfo = tileInfos_[ti];
                tileInfo.tileVisible = false;
            }
            // appear
            for(const auto  ti: appeared){
                auto & tileInfo = tileInfos_[ti];
                tileInfo.tileVisible = true;
                tileInfo.scrollCoordinate = scrollCoordinate_;
                tileInfo.timeCoordinate = timeCoordinate_;
                tileInfo.roi2d = blocking2d_.blockBegin()[ti];

                Shape3 begin3d,end3d;
                begin3d[scrollAxis_] = scrollCoordinate_;
                end3d[scrollAxis_] = scrollCoordinate_+1;
                begin3d[viewAxis_[0]] = tileInfo.roi2d.begin()[0];
                begin3d[viewAxis_[1]] = tileInfo.roi2d.begin()[1];
                end3d[viewAxis_[0]] = tileInfo.roi2d.end()[0];
                end3d[viewAxis_[1]] = tileInfo.roi2d.end()[1];

                tileInfo.roi3d = Block3d(begin3d, end3d);
            }
        }

    }

    size_t nVisibleTiles()const{
        return visibleBlocksManager_.visibleBlocks().size();
    }


    template<class OUT_ITER>
    void visibleTiles(OUT_ITER begin, OUT_ITER end)const{
        const auto & vt = visibleBlocksManager_.visibleBlocks();
        std::copy(vt.begin(), vt.end(), begin);
    }



    std::vector<size_t> 
    visibleTilesInRoi2D(
        Shape2d roiBegin,
        Shape2d roiEnd
    )const{
        std::vector<size_t> visibleTiles;
        const Block2d testBlock(roiBegin, roiEnd);
        for(const auto bi : visibleBlocksManager_.visibleBlocks()){
            const auto block = blocking2d_.blockBegin()[bi];
            if(testBlock.intersects(block)){
                visibleTiles.push_back(bi);
            }
        }
        return std::move(visibleTiles);
    }


    std::vector<size_t> 
    visibleTilesInRoi3D(
        Shape3 roiBegin,
        Shape3 roiEnd
    )const{
       if(roiBegin[scrollAxis_]<= scrollCoordinate_ && scrollCoordinate_<roiEnd[scrollAxis_]){
            const Shape2d roiBegin2D(roiBegin[viewAxis_[0]], roiBegin[viewAxis_[1]]);
            const Shape2d roiEnd2D(roiEnd[viewAxis_[0]], roiEnd[viewAxis_[1]]);
            return visibleTilesInRoi2D(roiBegin2D, roiEnd2D);
       }
       else{
            std::vector<size_t> res;
            return std::move(res);
       }
    }




    void updateScrollCoordinate(const uint64_t scrollCoordinate){
        scrollCoordinate_ = scrollCoordinate;
        for(auto ti : visibleBlocksManager_.visibleBlocks()){
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
        for(auto ti : visibleBlocksManager_.visibleBlocks()){
            tileInfos_[ti].timeCoordinate = timeCoordinate_;
        }
    }
    const Blocking2d  blocking2d_;
    size_t scrollAxis_;
    Shape2d viewAxis_;
    VisibleBlocksManager visibleBlocksManager_;


    uint64_t timeCoordinate_;
    uint64_t scrollCoordinate_;

    // infos per tile
    std::vector<TileInfo> tileInfos_;
};



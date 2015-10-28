

typedef vigra::MultiBlocking<2> Blocking2d;
typedef typename Blocking2d::Shape Shape2d;
typedef typename Blocking2d::Block Block2d;
typedef vigra::TinyVector<float, 2> Float2;
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
    :   blocking2d_(blocking2d_){
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

    }

    const std::vector<size_t> visibleBlocks()const{
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

    void updateScrollCoordinate(const uint64_t scrollCoordinate){
    }

    void updateTimeCoordinate(const uint64_t timeCoordinate){

    }

    bool tileVisible_;
    Block3d roi2d;
    Block3d roi3d;
    uint64_t scrollCoordinate;
    uint64_t timeCoordinate;
};


class TileGrid{
public:
    TileGrid(
        const Blocking2d & blocking2d,
        const Shape2d & tilingShape 
    )
    :   blocking2d_(blocking2d){
        tilingShape_(tilingShape),
        visibleBlocksManager_(blocking2d,tilingShape)
    {
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
        visibleBlocks_(begin, end, appeared,disappeared);
    }

    void updateScrollCoordinate(const uint64_t scrollCoordinate){
        scrollCoordinate_ = scrollCoordinate;
        for(auto bi : visibleBlocksManager_.visibleBlocks()){
            const auto ti = blockIndexToTileIndex_[bi];
            tileInfos_.updateScrollCoordinate(scrollCoordinate);
        }
    }

    void updateTimeCoordinate(const uint64_t timeCoordinate){
        timeCoordinate_ = timeCoordinate;
        for(auto bi : visibleBlocksManager_.visibleBlocks()){
            const auto ti = blockIndexToTileIndex_[bi];
            tileInfos_.updateTimeCoordinate(scrollCoordinate);
        }
    }

private:
    const Blocking2d & blocking2d_;
    Shape2d tilingShape_;
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








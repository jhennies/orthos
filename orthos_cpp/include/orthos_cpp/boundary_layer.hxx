

typedef std::pair<uint64_t, uint64_t> Edge;
typedef std::pair<uint8_t, uint32_t>  TileInViewer;


/**
 * @brief      for each edge (u,v) we keep
 *             track in which viewer and which tile in the particular viewer
 *             the edge is visible
 */
class EdgeVisibleInTiles{

public:

private:
    std::map<Edge, std::vector<TileInViewer> > map_;
};







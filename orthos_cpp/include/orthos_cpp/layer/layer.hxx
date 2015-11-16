

class DataSourceBase{
public:
};


class ArrayDataSourceBase : public DataSourceBase{
public:
};






/**
 * @brief      the layer class is the class which stands
 *             between the data sources and the tile items
 */
class LayerBase{
public:
    // query
    
    /**
     * @brief      name of the layer, the name must
     *             be unique, therefore no other layer
     *             should have this name
     *
     * @return     name of the layer
     */
    virtual std::string name() const = 0;

    /**
     * @brief      id of the layer, the id must be unique
     *
     * @return     id of the layer
     */
    virtual uint64_t id()const=0;

    /**
     * @brief      get the current alpha of this layer
     *
     * @return     alpha value in between  0 and 1
     */

    virtual float alpha() const = 0;

    /**
     * @brief      get the current visible state of the layer
     *
     * @return     true if visible false if not
     */
    virtual bool visible() const = 0;


    /**
     * @brief      is the layer currently occluding all layers below?
     *             This can only be true if alpha is 1.0 and visible is true.
     *             
     * @return     true if layer is occluding
     */
    virtual bool isOccluding() const = 0;

private:



};





class PixelLayerBase : public LayerBase{

public:

private:

};








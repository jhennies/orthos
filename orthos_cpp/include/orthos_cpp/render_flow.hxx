



namespace orthos{




    struct SliceRequest{
        //
    };

    /**
     * @brief      the data source itself 
     *             is the only "guy" who knows
     *             what is the suitable "sliceData" class.
     *             
     */
    class SliceDataSourceBase{
    public:
        virtual SliceDataBase * createSliceDataInstance()const = 0;
        virtual void fillSliceData(const SliceRequest & rq, SliceDataBase * sliceData);
    };


    class SliceDataBase{
    
    public:

    private:

    };


    template<class DATA_TYPE>
    class SliceData : public SliceDataBase{

    };



    class LutBase{
    };


}

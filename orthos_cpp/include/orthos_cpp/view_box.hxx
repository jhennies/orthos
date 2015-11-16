




struct Axis{

};


struct InputShape{

    std::vector<size_t> axisShape_;
    std::vector<std::string> axisName_;

};


struct ViewBoxCpp{
    
    public:

    private:
        // last axis is the scroll axis
        vigra::TinyVector<size_t, 3> axis_:
        const InputShape & inputShape_;
};

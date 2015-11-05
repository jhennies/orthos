#include <vigra/multi_array.hxx>
#include <cmath>



typedef vigra::TinyVector<unsigned char, 4> UChar4;


template<class T>
T clip(const T  t, const T minVal, const T maxVal){
    return  std::min(std::max(t, minVal), maxVal);
}


template<class T>
uint64_t normalizeToIndex(const T & t, const T minVal, const T maxVal, const uint64_t nBins){
    const auto clippedVal = clip(t, minVal, maxVal);
    /*use promotes*/
    const auto fbin = (double(clippedVal)- double(minVal) )/double(maxVal-minVal)*(nBins-1);
    return static_cast<uint64_t>(fbin);
}



namespace to_rgba{


    template<class F>
    struct NormalizedExplicitLut{
    public:
        typedef UChar4 value_type;
        UChar4 operator[](const F  val)const{
            //std::cout<<"elut "<<elut_.size()<<" min "<<int(min_)<<" max "<<int(max_)<<"\n";
            const auto index = normalizeToIndex(val, min_, max_, elut_.size());
            //std::cout<<"index "<<index<<"\n";
            return elut_[index];
        }

        F min_;
        F max_;

        vigra::MultiArray<1, UChar4> elut_;
    };

    template<class F>
    struct NormalizedGray{

        typedef UChar4 value_type;
        UChar4 operator[](const F  val)const{
            return UChar4(normalizeToIndex(val, min_, max_, 256));
        }
        F min_;
        F max_;
    };

    struct Gray{
        typedef UChar4 value_type;
        UChar4 operator[](const uint8_t  val){
            return UChar4(val);
        }
    };




    template<class T_IN,  class LUT>
    void applyLut(
        const vigra::MultiArrayView<1, T_IN> & imageIn,
        const LUT & lut,
        vigra::MultiArrayView<1, typename LUT::value_type> & imageOut
    ){
        //std::cout<<"apply lut\n";
        auto inIter = imageIn.begin();
        auto outIter = imageOut.begin();
        for(size_t i=0; i<imageIn.size();++i,++inIter,++outIter){
            *outIter = lut[*inIter];
        }
        //std::cout<<"apply lut done\n";
    }

    template<class T_IN,  class LUT>
    void applyLut2D(
        const vigra::MultiArrayView<2, T_IN> & imageIn,
        const LUT & lut,
        vigra::MultiArrayView<2, typename LUT::value_type> & imageOut
    ){
        //std::cout<<"apply lut\n";
        auto inIter = imageIn.begin();
        auto outIter = imageOut.begin();
        for(size_t i=0; i<imageIn.size();++i,++inIter,++outIter){
            *outIter = lut[*inIter];
        }
        //std::cout<<"apply lut done\n";
    }

}

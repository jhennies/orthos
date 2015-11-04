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
        UChar4 operator[](const F  val){
            return lut_[normalizeToIndex(val, min_, max_, lut_.size())];
        }

        F min_;
        F max_;

        vigra::MultiArrayView<1, UChar4> lut_;
    };

    template<class F>
    struct NormalizedGray{

        typedef UChar4 value_type;
        UChar4 operator[](const F  val){
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

}

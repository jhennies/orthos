#include <vigra/multi_array.hxx>
#include <cmath>

typedef vigra::TinyVector<unsigned char, 3> UChar3;
typedef vigra::TinyVector<unsigned char, 4> UChar4;

struct RGBA_Tag{};
struct ARGB_Tag{};



template<class F, class U>
class FloatToUInt{
public:
    typedef U value_type;
    FloatToUInt(const F  minVal, const F  maxVal)
    :   minVal_(minVal),
        maxVal_(maxVal){

    }

    template<class FKEY>
    value_type operator[](const FKEY & key)const{
        F fkey = key;
        fkey -= minVal_;
        fkey /= (maxVal_-minVal_);
        return U(fkey*std::numeric_limits<U>::max());
    }
private:
    F minVal_;
    F maxVal_;
};


template<class LUT_1, class LUT_2>
class FloatToLut{

public:

private:
    const LUT_1 & lut1_;
    const LUT_2 lut_2;
};






template<unsigned int CHANNELS>
class IntToRandRgbLut{
public:
    typedef vigra::TinyVector<unsigned char, CHANNELS> value_type;

    template<class UINT_KEY>
    value_type operator[](const UINT_KEY  key)const{
        value_type res;
        for(auto c=0; c<CHANNELS; ++c){
            auto fkey = std::sin(float(key+offset_))*1000.0+c;
            res[c] = hash_(fkey ) %256;
        }
        return res;
    }
private:
    std::hash<float> hash_;
    size_t offset_;
};

template<class VALUE_TYPE>
class MultiArrayViewLut{
public:
    typedef VALUE_TYPE value_type;
private:
    template<class UINT_KEY>
    value_type operator[](const UINT_KEY  key)const{
        return lut_[key];
    }
    vigra::MultiArrayView<1, value_type> lut_;
};


template<class MAP, class LUT>
class SparseMapLut{
public:
    typedef MAP Map;
    typedef LUT Lut;
    typedef typename MAP::key_type MapKey;
    typedef typename MAP::mapped_type MapValueType;
    typedef typename  LUT::value_type value_type;

    SparseMapLut(const Map & map, const Lut & lut,const MapValueType  defaultMapVal)
    :   map_(map),
        lut_(lut),
        defaultMapVal_(defaultMapVal){
    }

    template<class KEY>
    value_type operator[](const KEY key)const{
        std::cout<<" lut key "<<key<<"\n";
        auto iter = map_.find(static_cast<MapKey>(key));
        if(iter == map_.end()){
            std::cout<<"not in map\n";
            return lut_[defaultMapVal_];
        }
        else{
            std::cout<<"    in map\n";
            return lut_[iter->second];
        }
    }
private:
    const MAP & map_;
    const LUT  lut_;
    const MapValueType defaultMapVal_;
};





template<class T_IN,  class LUT>
void applyLut(
    vigra::MultiArrayView<1, T_IN> & imageIn,
    const LUT & lut,
    vigra::MultiArrayView<1, typename LUT::value_type> imageOut
){
    auto inIter = imageIn.begin();
    auto outIter = imageOut.begin();
    for(size_t i=0; i<imageIn.size();++i,++inIter,++outIter){
        *outIter = lut[*inIter];
    }
}

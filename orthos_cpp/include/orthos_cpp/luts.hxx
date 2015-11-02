#include <vigra/multi_array.hxx>

typedef vigra::TinyVector<unsigned char, 3> UChar3;
typedef vigra::TinyVector<unsigned char, 4> UChar4;


template<class KEY, unsigned int CHANNELS>
class IntToRandRgbLut{
public:
    typedef KEY Key;
    typedef vigra::TinyVector<unsigned char, CHANNELS> ValueType;

    ValueType operator[](const Key & key)const{
        ValueType res;
        for(auto c=0; c<CHANNELS; ++c)
            res[c] = hash_(offset_ + c+key*c)%256;
        return key;
    }
private:
    std::hash<Key> hash_;
    size_t offset_;
};

template<class VALUE_TYPE, class INTEGRAL_KEY>
class MultiArrayViewLut{
public:
    typedef INTEGRAL_KEY Key;
    typedef VALUE_TYPE ValueType;
private:
    ValueType operator[](const Key & key)const{
        return lut_[key];
    }
    vigra::MultiArrayView<1, ValueType> lut_;
};


template<class MAP, class LUT>
class SparseMapLut{
public:
    typedef MAP Map;
    typedef LUT Lut;
    typedef typename MAP::key_type Key;
    typedef typename MAP::mapped_type MapValueType;
    typedef typename  LUT::ValueType ValueType;

    SparseMapLut(const Map & map, const Lut & lut,const MapValueType  defaultMapVal)
    :   map_(map),
        lut_(lut),
        defaultMapVal_(defaultMapVal){
    }

    ValueType operator[](const Key & key)const{
        auto iter = map_.find(key);
        if(iter == map_.end())
            return lut_[defaultMapVal_];
        else
            return lut_[iter->second];
    }
private:
    const MAP & map_;
    const LUT & lut_;
    const MapValueType defaultMapVal_;
};





template<class T_IN,  class LUT>
void applyLut(
    vigra::MultiArrayView<1, T_IN> & imageIn,
    const LUT & lut,
    vigra::MultiArrayView<1, typename LUT::ValueType> imageOut
){
    auto inIter = imageIn.begin();
    auto outIter = imageOut.begin();
    for(size_t i=0; i<imageIn.size();++i,++inIter,++outIter){
        *outIter = lut[*inIter];
    }
}

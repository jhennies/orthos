/************************************************************************/
/*                                                                      */
/*                 Copyright 2011 by Ullrich Koethe                     */
/*                                                                      */
/*    This file is part of the VIGRA computer vision library.           */
/*    The VIGRA Website is                                              */
/*        http://hci.iwr.uni-heidelberg.de/vigra/                       */
/*    Please direct questions, bug reports, and contributions to        */
/*        ullrich.koethe@iwr.uni-heidelberg.de    or                    */
/*        vigra@informatik.uni-hamburg.de                               */
/*                                                                      */
/*    Permission is hereby granted, free of charge, to any person       */
/*    obtaining a copy of this software and associated documentation    */
/*    files (the "Software"), to deal in the Software without           */
/*    restriction, including without limitation the rights to use,      */
/*    copy, modify, merge, publish, distribute, sublicense, and/or      */
/*    sell copies of the Software, and to permit persons to whom the    */
/*    Software is furnished to do so, subject to the following          */
/*    conditions:                                                       */
/*                                                                      */
/*    The above copyright notice and this permission notice shall be    */
/*    included in all copies or substantial portions of the             */
/*    Software.                                                         */
/*                                                                      */
/*    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND    */
/*    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES   */
/*    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND          */
/*    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT       */
/*    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,      */
/*    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING      */
/*    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR     */
/*    OTHER DEALINGS IN THE SOFTWARE.                                   */
/*                                                                      */
/************************************************************************/

#define PY_ARRAY_UNIQUE_SYMBOL vigranumpyorthos_PyArray_API
//#define NO_IMPORT_ARRAY

// Include this first to avoid name conflicts for boost::tie,
// similar to issue described in vigra#237
//#include <boost/tuple/tuple.hpp>

/*orthos*/
#include <orthos_cpp/orthos.hxx>
#include <orthos_cpp/tilegrid_2d.hxx>
#include <orthos_cpp/luts.hxx>
/*vigra python */
#include <vigra/numpy_array.hxx>
#include <vigra/numpy_array_converters.hxx>

#include <boost/python/suite/indexing/map_indexing_suite.hpp>

namespace python = boost::python;












vigra::NumpyAnyArray 
applyDrawKernel(
    vigra::NumpyArray<2,vigra::UInt8> labelImage,
    vigra::NumpyArray<2,vigra::UInt8> drawKernel,
    vigra::NumpyArray<2,vigra::UInt8> output
){
    int rx = (drawKernel.shape(0) - 1)/2;
    int ry = (drawKernel.shape(1) - 1)/2;
    std::cout<<"rx "<<rx<<" rx"<<"\n";
    for(int y=0; y<labelImage.shape(1); ++y)
    for(int x=0; x<labelImage.shape(0); ++x){
        if(labelImage(x,y)!=0){
            for(int ky=0; ky<drawKernel.shape(1); ++ky)
            for(int kx=0; kx<drawKernel.shape(0); ++kx){
                if( x+kx-rx >0 && x+kx-rx <labelImage.shape(0)  &&
                    y+ky-ry >0 && y+ky-ry <labelImage.shape(1) ){
                    if(drawKernel(kx,ky)!=0){
                        output(x+kx-rx,y+ky-ry) = labelImage(x,y);
                    }
                }
            }
        }
    }
    return output;
}



void exportDrawing(){
    python::def("applyDrawKernel2d",vigra::registerConverters(&applyDrawKernel))
    ;
}



python::tuple 
updateCurrentRoi(
    TileGridManager & tgm,
    const Float2 & begin,
    const Float2 & end
){
    std::vector<size_t > a,d;
    tgm.updateCurrentRoi(begin, end, a,d);
    vigra::NumpyArray<1,uint64_t> an(Shape1(a.size())),dn(Shape1(d.size()));
    std::copy(a.begin(),a.end(),an.begin());
    std::copy(d.begin(),d.end(),dn.begin());
    return python::make_tuple(an,dn);
}


vigra::NumpyAnyArray
visibleBlocks(const TileGridManager &tgm){
    vigra::NumpyArray<1,uint64_t> vb(Shape1(tgm.nVisibleTiles()));
    tgm.visibleBlocks(vb.begin(), vb.end());
    return vb;
}

vigra::NumpyAnyArray
visibleTiles(const TileGridManager &tgm){
    vigra::NumpyArray<1,uint64_t> vb(Shape1(tgm.nVisibleTiles()));
    tgm.visibleTiles(vb.begin(), vb.end());
    return vb;
}



vigra::NumpyAnyArray
visibleTilesInRoi2D(
    const TileGridManager &tgm,
    const Shape2 & roiBegin,
    const Shape2 & roiEnd
){
    const auto vt = tgm.visibleTilesInRoi2D(roiBegin, roiEnd);
    vigra::NumpyArray<1,uint64_t> vta(Shape1(vt.size()));
    std::copy(vt.begin(),vt.end(),vta.begin());
    return vta;
}

vigra::NumpyAnyArray
visibleTilesInRoi3D(
    const TileGridManager &tgm,
    const Shape3 & roiBegin,
    const Shape3 & roiEnd
){
    const auto vt = tgm.visibleTilesInRoi3D(roiBegin, roiEnd);
    vigra::NumpyArray<1,uint64_t> vta(Shape1(vt.size()));
    std::copy(vt.begin(),vt.end(),vta.begin());
    return vta;
}




void exportTileGrid(){
    python::class_<TileGridManager>(
        "TileGridManager",
        python::init<const Blocking2d &, const Shape2d, size_t,const Shape2d>()
    )
        .def("updateTimeCoordinate",&TileGridManager::updateTimeCoordinate)
        .def("updateScrollCoordinate",&TileGridManager::updateScrollCoordinate)
        .def("updateCurrentRoi",vigra::registerConverters(updateCurrentRoi))
        .def("tileInfo",&TileGridManager::tileInfo,python::return_internal_reference<>())
        .def("nVisibleTiles",&TileGridManager::nVisibleTiles)
        .def("visibleBlocks",vigra::registerConverters(&visibleBlocks))
        .def("visibleTiles",vigra::registerConverters(&visibleTiles))
        .def("visibleTilesInRoi2D",vigra::registerConverters(&visibleTilesInRoi2D))
        .def("visibleTilesInRoi3D",vigra::registerConverters(&visibleTilesInRoi3D))
    ;

    python::class_<TileInfo>("TileInfo",python::init<>())
        .def("copy",&TileInfo::copy)
        .def_readonly("tileVisible", &TileInfo::tileVisible)
        .def_readonly("roi2d", &TileInfo::roi2d)
        .def_readonly("roi3d", &TileInfo::roi3d)
        .def_readonly("scrollCoordinate", &TileInfo::scrollCoordinate)
        .def_readonly("timeCoordinate", &TileInfo::timeCoordinate)
        .def("__eq__", &TileInfo::operator==)
        .def("__neq__", &TileInfo::operator!=)
    ;    
}

template<class K, class V>
void exportMapT(const std::string & clsName){
    typedef std::map<K,V> Map;
    python::class_<Map>(clsName.c_str())
        .def(python::map_indexing_suite<Map>() );
}


void exportMaps(){

    typedef vigra::TinyVector<uint64_t, 2> V2UInt64;
    
    exportMapT<V2UInt64, uint8_t >("Map_From_V2UInt64_To_Uint8");
    exportMapT<uint64_t, uint8_t >("Uint64_Uint8_Map");
}



template<class T_IN, class LUT>
vigra::NumpyAnyArray 
pyApplyLut(
    vigra::NumpyArray<1, T_IN> dataIn,
    const LUT & lut,
    vigra::NumpyArray<1, typename LUT::value_type> out
){
    out.reshapeIfEmpty(dataIn.shape());
    applyLut(dataIn, lut, out);
    return out;
}




template<class T_IN, class LUT>
void exportApplyLut(){
    python::def(
        "applyLut", 
        vigra::registerConverters(&pyApplyLut<T_IN, LUT>),
        (
            python::arg("data"),
            python::arg("lut"),
            python::arg("out") = python::object()
        )
    );
}

template<class LUT>
void exportRandomLutClass(const std::string & clsName){

    {
        typedef LUT Lut;
        python::class_<Lut>(clsName.c_str(),python::init<>())
        ;
    }
}

template<class LUT>
void exportFloatToUInt(const std::string & clsName){

    {
        typedef LUT Lut;
        python::class_<Lut>(clsName.c_str(),python::init<const float,const float>())
        ;
    }
}

template<class LUT, class SUBLUT>
void exportMapLut(const std::string & clsName){

    {
        typedef LUT Lut;
        typedef typename Lut::Map Map;
        typedef typename Lut::MapValueType MapValueType;
        typedef typename Lut::Lut SubLut;

        python::class_<Lut>(clsName.c_str(),
            python::init<const Map &, const SUBLUT & ,const MapValueType>()
        )
        ;
    }
}





void exportLutFunctions(){


    // float32 to uint8
    {
        typedef FloatToUInt<float,uint8_t> Lut;
        exportFloatToUInt<Lut>("Float32ToUInt8Lut");
        exportApplyLut<float, Lut>();
    }
    // float64 to uint8
    {
        typedef FloatToUInt<double,uint8_t> Lut;
        exportFloatToUInt<Lut>("Float64ToUInt8Lut");
        exportApplyLut<double, Lut>();
    }
    
    // random lut
    {
        typedef IntToRandRgbLut<3> Lut;
        exportRandomLutClass<Lut>("RandomLut3");
        //exportApplyLut<uint8_t, Lut>();
        //exportApplyLut<uint16_t, Lut>();
        exportApplyLut<uint32_t, Lut>();
        //exportApplyLut<uint64_t, Lut>();
    }
    // explicit lut 3
    {
        typedef  vigra::NumpyArray<1, UChar3> ExplicitLut;
        exportApplyLut<uint32_t, ExplicitLut>();
    }
    // explicit lut 4
    {
        typedef  vigra::NumpyArray<1, UChar4> ExplicitLut;
        exportApplyLut<uint32_t, ExplicitLut>();
    }

    // export map luts
    {
        // map from uint64 to "object label" aka uint8
        typedef std::map<uint64_t, uint8_t > Map;
        typedef  vigra::NumpyArray<1, UChar3> ExplicitLut;
        typedef  vigra::MultiArrayView<1, UChar3> ViewExplicitLut;

        typedef SparseMapLut<Map, ViewExplicitLut> Lut;
        exportMapLut<Lut,ExplicitLut>("SparseMapLut");
        exportApplyLut<uint32_t, Lut>();
    }
}


BOOST_PYTHON_MODULE_INIT(_orthos_cpp)
{
    vigra::import_vigranumpy();

    python::docstring_options doc_options(true, true, false);


    exportDrawing();
    exportTileGrid();
    exportLutFunctions();
    exportMaps();
}



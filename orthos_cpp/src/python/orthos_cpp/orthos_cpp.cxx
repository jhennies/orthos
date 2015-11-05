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
#include <orthos_cpp/new_lut.hxx>
/*vigra python */
#include <vigra/numpy_array.hxx>
#include <vigra/numpy_array_converters.hxx>
#include <vigra/python_utility.hxx>
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
vigra::NumpyAnyArray pyApplyLut2D(
    const vigra::NumpyArray<2, T_IN> & data,
    const LUT & lut,
    vigra::NumpyArray<2, typename LUT::value_type>  out
){
    out.reshapeIfEmpty(data.shape());
    {
        vigra::PyAllowThreads _pythread;
        to_rgba::applyLut2D(data, lut, out);
    }
    return out;
}

template<class T_IN, class LUT>
void exportApplyLut(){

    python::def("applyLut2D",vigra::registerConverters(&pyApplyLut2D<T_IN, LUT>),
        (
            python::arg("data"),
            python::arg("lut"),
            python::arg("out") = python::object()
        )
    );
}

template<class LUT>
void setLutArray(
    LUT & lut,
    const vigra::NumpyArray<1, UChar4> & elut
){
    std::cout<<"SET LUT ARRAY \n";
    std::cout<<"input shape "<<elut.shape()<<"\n";
    lut.elut_ = elut;
}


template<class T>
void exportNormalizedExplicitLut(
    const std::string & clsName
){
    typedef to_rgba::NormalizedExplicitLut<T> Lut;

    python::class_<Lut>(clsName.c_str(), python::init<>())
        .def("__call__",&Lut::operator[])
        .def("setMinMax", &Lut::setMinMax)
        .def_readonly("hasMinMax", &Lut::hasMinMax_)
        .def("setLutArray",vigra::registerConverters(&setLutArray<Lut>))
    ;

    exportApplyLut<T, Lut>();
}


template<class T>
void exportNormalizedGray(
    const std::string & clsName
){
    typedef to_rgba::NormalizedGray<T> Lut;

    python::class_<Lut>(clsName.c_str(), python::init<>())
        .def("__call__",&Lut::operator[])
        .def("setMinMax", &Lut::setMinMax)
        .def_readonly("hasMinMax", &Lut::hasMinMax_)
    ;
    exportApplyLut<T, Lut>();
}











void exportLuts(){

    exportNormalizedExplicitLut<float>("NormalizedExplicitLut_float32");
    exportNormalizedExplicitLut<double>("NormalizedExplicitLut_float64");
    exportNormalizedExplicitLut<uint8_t>("NormalizedExplicitLut_uint8");
    exportNormalizedExplicitLut<uint16_t>("NormalizedExplicitLut_uint16");
    exportNormalizedExplicitLut<uint32_t>("NormalizedExplicitLut_uint32");
    exportNormalizedExplicitLut<uint64_t>("NormalizedExplicitLut_uint64");
    exportNormalizedExplicitLut<int8_t>("NormalizedExplicitLut_int8");
    exportNormalizedExplicitLut<int16_t>("NormalizedExplicitLut_int16");
    exportNormalizedExplicitLut<int32_t>("NormalizedExplicitLut_int32");
    exportNormalizedExplicitLut<int64_t>("NormalizedExplicitLut_int64");


    exportNormalizedGray<float>("NormalizedGray_float32");
    exportNormalizedGray<double>("NormalizedGray_float64");
    exportNormalizedGray<uint8_t>("NormalizedGray_uint8");
    exportNormalizedGray<uint16_t>("NormalizedGray_uint16");
    exportNormalizedGray<uint32_t>("NormalizedGray_uint32");
    exportNormalizedGray<uint64_t>("NormalizedGray_uint64");
    exportNormalizedGray<int8_t>("NormalizedGray_int8");
    exportNormalizedGray<int16_t>("NormalizedGray_int16");
    exportNormalizedGray<int32_t>("NormalizedGray_int32");
    exportNormalizedGray<int64_t>("NormalizedGray_int64");
}






BOOST_PYTHON_MODULE_INIT(_orthos_cpp)
{
    vigra::import_vigranumpy();

    python::docstring_options doc_options(true, true, false);


    exportDrawing();
    exportTileGrid();
    exportMaps();
    exportLuts();
}



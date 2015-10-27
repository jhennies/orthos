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

#define PY_ARRAY_UNIQUE_SYMBOL vigranumpyilastiktools_PyArray_API
//#define NO_IMPORT_ARRAY

// Include this first to avoid name conflicts for boost::tie,
// similar to issue described in vigra#237
#include <boost/tuple/tuple.hpp>

/*vigra*/
#include <orthos_cpp/orthos.hxx>


/*vigra python */
#include <vigra/numpy_array.hxx>
#include <vigra/numpy_array_converters.hxx>



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



BOOST_PYTHON_MODULE_INIT(_orthos_cpp)
{
    vigra::import_vigranumpy();

    python::docstring_options doc_options(true, true, false);
    python::def("applyDrawKernel2d",vigra::registerConverters(&applyDrawKernel))
    ;
}



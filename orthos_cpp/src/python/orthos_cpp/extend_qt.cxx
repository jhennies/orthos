#define PY_ARRAY_UNIQUE_SYMBOL vigranumpyorthos_PyArray_API
#define NO_IMPORT_ARRAY


/*orthos*/
#include <orthos_cpp/orthos.hxx>
#include <orthos_cpp/tilegrid_2d.hxx>
#include <orthos_cpp/new_lut.hxx>
/*vigra python */
#include <vigra/numpy_array.hxx>
#include <vigra/numpy_array_converters.hxx>
#include <vigra/python_utility.hxx>
#include <boost/python/suite/indexing/map_indexing_suite.hpp>

/*qt*/

#include <QObject>
#include <QWidget>
#include <QFrame>
#include <QLabel>


namespace python = boost::python;




long int unwrap(QObject* ptr) {
    return reinterpret_cast<long int>(ptr);
}

template <typename T>
T* wrap(long int ptr) {
    return reinterpret_cast<T*>(ptr);
}






template<class QT_CLASS>
void exportExisiting(const std::string & clsName){

    python::class_<QT_CLASS, QT_CLASS*, boost::noncopyable>(clsName.c_str(), python::no_init)
        .def("unwrap", unwrap)
        .def("wrap", 
            python::make_function( 
                wrap<QT_CLASS>, 
                python::return_value_policy<python::return_by_value>() 
            )
        )
        .staticmethod("wrap");
    ;
}

template<class QT_CLASS, class BASE_CLASS>
void exportExisitingWithBase(const std::string & clsName){

    python::class_<QT_CLASS, python::bases<BASE_CLASS>, QT_CLASS*, boost::noncopyable>(clsName.c_str())
        //.def("wrap", 
        //    python::make_function( 
        //        wrap<QT_CLASS>, 
        //        python::return_value_policy<python::return_by_value>() 
        //    )
        //)
        //.staticmethod("wrap");
    ;
}

void extendQt(){
    exportExisiting<QObject>("QObject");
    exportExisitingWithBase<QWidget,QObject>("QWidget");
    exportExisitingWithBase<QFrame,QWidget>("QFrame");
    exportExisitingWithBase<QLabel,QFrame>("QLabel");
}

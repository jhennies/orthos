#define PY_ARRAY_UNIQUE_SYMBOL vigranumpyorthos_PyArray_API
#define NO_IMPORT_ARRAY


/*orthos*/
#include <orthos_cpp/orthos.hxx>
#include <orthos_cpp/layer/layer.hxx>
/*vigra python */
#include <vigra/numpy_array.hxx>
#include <vigra/numpy_array_converters.hxx>
#include <vigra/python_utility.hxx>
#include <boost/python/suite/indexing/map_indexing_suite.hpp>

namespace python = boost::python;

struct LayerBaseWrap : LayerBase, python::wrapper<LayerBase>
{
    std::string name() const {
        return this->get_override("name")();
    }

    uint64_t id() const {
        return this->get_override("id")();
    }

    float alpha() const {
        return this->get_override("alpha")();
    }

    bool visible() const {
        return this->get_override("visible")();
    }

    bool isOccluding() const {
        return this->get_override("isOccluding")();
    }

};



void exportLayer(){

    python::class_<LayerBaseWrap, boost::noncopyable>("LayerBase")
        .def("name", python::pure_virtual(&LayerBase::name))
    ;


}

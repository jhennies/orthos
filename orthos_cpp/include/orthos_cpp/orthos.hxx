#ifndef ORTHOS_CPP_ORTHOS_HXX
#define ORTHOS_CPP_ORTHOS_HXX

#include <vigra/adjacency_list_graph.hxx>
#include <vigra/timing.hxx>
#include <vigra/multi_gridgraph.hxx>
#include <vigra/multi_array.hxx>
#include <vigra/tinyvector.hxx>
#include <vigra/timing.hxx>
#include <vigra/graph_algorithms.hxx>


namespace orthos{

typedef vigra::TinyVector<unsigned char, 4> UChar4;
typedef vigra::MultiArrayView<2, UChar4> RGBAImageView;


}

#endif /*ORTHOS_CPP_ORTHOS_HXX*/

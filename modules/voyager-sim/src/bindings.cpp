#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "voyager/sim/State.hpp"
#include "voyager/sim/RigidBody.hpp"

namespace py = pybind11;
using namespace voyager::sim;

class VoyagerSimEngine {
public:
    RigidBody rb;
    State state;

    VoyagerSimEngine() : rb(), state() {}
    VoyagerSimEngine(double mass, double Ixx, double Iyy, double Izz)
        : rb(mass, Ixx, Iyy, Izz), state() {}

    void step(const Inputs& inputs, double dt) {
        rb.stepRK4(state, inputs, dt);
    }

    void reset() {
        state = State();
    }

    void reset_to(double x, double y, double z, double qw = 1.0, double qx = 0.0, double qy = 0.0, double qz = 0.0) {
        state = State();
        state.x = x;
        state.y = y;
        state.z = z;
        state.qw = qw;
        state.qx = qx;
        state.qy = qy;
        state.qz = qz;
        state.normalizeQuaternion();
    }

    const State& getState() const {
        return state;
    }

    void setState(const State& s) {
        state = s;
    }
};

PYBIND11_MODULE(voyager_sim_py, m) {
    m.doc() = "Python bindings for Voyager Sim 6-DOF physics engine";

    py::class_<State>(m, "State")
        .def(py::init<>())
        .def_readwrite("x", &State::x)
        .def_readwrite("y", &State::y)
        .def_readwrite("z", &State::z)
        .def_readwrite("vx", &State::vx)
        .def_readwrite("vy", &State::vy)
        .def_readwrite("vz", &State::vz)
        .def_readwrite("qw", &State::qw)
        .def_readwrite("qx", &State::qx)
        .def_readwrite("qy", &State::qy)
        .def_readwrite("qz", &State::qz)
        .def_readwrite("p", &State::p)
        .def_readwrite("q", &State::q)
        .def_readwrite("r", &State::r)
        .def("toArray", &State::toArray)
        .def("fromArray", &State::fromArray)
        .def("normalizeQuaternion", &State::normalizeQuaternion)
        .def("__repr__", [](const State& s) {
            return "<State pos=(" + std::to_string(s.x) + ", " + std::to_string(s.y) + ", " + std::to_string(s.z) +
                   ") vel=(" + std::to_string(s.vx) + ", " + std::to_string(s.vy) + ", " + std::to_string(s.vz) + ")>";
        });

    py::class_<Inputs>(m, "Inputs")
        .def(py::init<>())
        .def(py::init([](double total_thrust, double tau_x, double tau_y, double tau_z) {
            auto inp = std::make_unique<Inputs>();
            inp->total_thrust = total_thrust;
            inp->tau_x = tau_x;
            inp->tau_y = tau_y;
            inp->tau_z = tau_z;
            return inp;
        }), py::arg("total_thrust") = 0.0, py::arg("tau_x") = 0.0, py::arg("tau_y") = 0.0, py::arg("tau_z") = 0.0)
        .def_readwrite("total_thrust", &Inputs::total_thrust)
        .def_readwrite("tau_x", &Inputs::tau_x)
        .def_readwrite("tau_y", &Inputs::tau_y)
        .def_readwrite("tau_z", &Inputs::tau_z)
        .def("__repr__", [](const Inputs& inp) {
            return "<Inputs thrust=" + std::to_string(inp.total_thrust) +
                   " tau=(" + std::to_string(inp.tau_x) + ", " + std::to_string(inp.tau_y) + ", " + std::to_string(inp.tau_z) + ")>";
        });

    py::class_<RigidBody>(m, "RigidBody")
        .def(py::init<>())
        .def(py::init<double, double, double, double>(),
             py::arg("mass"), py::arg("Ixx"), py::arg("Iyy"), py::arg("Izz"))
        .def_readwrite("mass", &RigidBody::mass)
        .def_readwrite("g", &RigidBody::g)
        .def_readwrite("Ixx", &RigidBody::Ixx)
        .def_readwrite("Iyy", &RigidBody::Iyy)
        .def_readwrite("Izz", &RigidBody::Izz)
        .def_readwrite("C_drag_xy", &RigidBody::C_drag_xy)
        .def_readwrite("C_drag_z", &RigidBody::C_drag_z)
        .def_readwrite("C_rot", &RigidBody::C_rot)
        .def("computeDerivatives", &RigidBody::computeDerivatives)
        .def("stepEuler", &RigidBody::stepEuler)
        .def("stepRK4", &RigidBody::stepRK4)
        .def_static("getRotationMatrix", &RigidBody::getRotationMatrix);

    py::class_<VoyagerSimEngine>(m, "VoyagerSimEngine")
        .def(py::init<>())
        .def(py::init<double, double, double, double>(),
             py::arg("mass"), py::arg("Ixx"), py::arg("Iyy"), py::arg("Izz"))
        .def_readwrite("rb", &VoyagerSimEngine::rb)
        .def_readwrite("state", &VoyagerSimEngine::state)
        .def("step", &VoyagerSimEngine::step, py::arg("inputs"), py::arg("dt"))
        .def("reset", &VoyagerSimEngine::reset)
        .def("reset_to", &VoyagerSimEngine::reset_to,
             py::arg("x"), py::arg("y"), py::arg("z"),
             py::arg("qw") = 1.0, py::arg("qx") = 0.0, py::arg("qy") = 0.0, py::arg("qz") = 0.0)
        .def("getState", &VoyagerSimEngine::getState)
        .def("setState", &VoyagerSimEngine::setState);
}

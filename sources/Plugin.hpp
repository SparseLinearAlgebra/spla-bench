/**********************************************************************************/
/* This file is part of spla project                                              */
/* https://github.com/JetBrains-Research/spla-bench                               */
/**********************************************************************************/
/* MIT License                                                                    */
/*                                                                                */
/* Copyright (c) 2021 JetBrains-Research                                          */
/*                                                                                */
/* Permission is hereby granted, free of charge, to any person obtaining a copy   */
/* of this software and associated documentation files (the "Software"), to deal  */
/* in the Software without restriction, including without limitation the rights   */
/* to use, copy, modify, merge, publish, distribute, sublicense, and/or sell      */
/* copies of the Software, and to permit persons to whom the Software is          */
/* furnished to do so, subject to the following conditions:                       */
/*                                                                                */
/* The above copyright notice and this permission notice shall be included in all */
/* copies or substantial portions of the Software.                                */
/*                                                                                */
/* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR     */
/* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,       */
/* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE    */
/* AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER         */
/* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  */
/* OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  */
/* SOFTWARE.                                                                      */
/**********************************************************************************/

#ifndef SPLA_BENCH_PLUGIN_HPP
#define SPLA_BENCH_PLUGIN_HPP

#include "Benchmark.hpp"
#include "BenchmarkEngine.hpp"

#include <memory>
#include <string>

namespace bench {

    class Plugin {
    public:
        virtual ~Plugin() = default;

        virtual std::shared_ptr<Benchmark> BenchmarkBfs() { return nullptr; };
        virtual std::shared_ptr<Benchmark> BenchmarkSssp() { return nullptr; };
        virtual std::shared_ptr<Benchmark> BenchmarkTc() { return nullptr; };
        virtual std::shared_ptr<Benchmark> BenchmarkCc() { return nullptr; };
        virtual std::shared_ptr<Benchmark> BenchmarkPageRank() { return nullptr; };

        virtual std::string GetName() = 0;
        virtual std::string GetDescription() = 0;
    };

}// namespace bench

/**
 * Use this macro to register your plugin into the system
 */
#define REGISTER_PLUGIN(PluginName, PluginClass)      \
    struct Register##PluginName {                     \
        Register##PluginName() noexcept {             \
            ::bench::BenchmarkEngine::Register(       \
                    std::shared_ptr<::bench::Plugin>( \
                            new PluginClass()));      \
        }                                             \
    };                                                \
    static Register##PluginName __register__##PluginName;

#endif//SPLA_BENCH_PLUGIN_HPP

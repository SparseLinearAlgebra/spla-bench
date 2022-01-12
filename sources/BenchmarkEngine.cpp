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

#include "BenchmarkEngine.hpp"
#include "Plugin.hpp"

#include <algorithm>
#include <cassert>
#include <iostream>

int bench::BenchmarkEngine::Run(int argc, const char *const *argv) {
    auto &engine = Instance();
    engine.Parse(argc, argv);
    return engine.Execute();
}

void bench::BenchmarkEngine::Register(const std::shared_ptr<Plugin> &plugin) {
    assert(plugin);
    auto &engine = Instance();
    engine.mPlugins.emplace(plugin->GetName(), plugin);
    std::cout << "Register plugin \"" << plugin->GetName() << "\"\n";
}

bench::BenchmarkEngine &bench::BenchmarkEngine::Instance() {
    static BenchmarkEngine gBenchmarkEngine;
    return gBenchmarkEngine;
}

void bench::BenchmarkEngine::Parse(int argc, const char *const *argv) {
    for (int i = 0; i < argc; i++)
        mOptions.emplace_back(argv[i]);
}

int bench::BenchmarkEngine::Execute() {
    return 0;
}
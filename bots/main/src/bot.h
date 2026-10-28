#pragma once
#include "strategy.h"

// Per-champion bot; the engine instance persists across turns.
class Bot {
    strat::Engine engine_;

public:
    void play_turn();
};

package com.barttolo.ringworldnether;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.Level;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.fml.common.Mod;

/** Standalone add-on. Install alongside the unmodified original RingWorld. */
@Mod(RingWorldNetherMod.MOD_ID)
public final class RingWorldNetherMod {
    public static final String MOD_ID = "ringworld_nether";
    public static final int NETHER_WIDTH = 1008;
    public static final int NETHER_CIRCUMFERENCE = 14976;
    public static final int NETHER_WALL_HEIGHT = 40;
    public static final double SPAWN_X = 142.5;
    public static final double SPAWN_Y = 84;
    public static final double SPAWN_Z = 0.5;

    public RingWorldNetherMod() {
        MinecraftForge.EVENT_BUS.addListener(this::onDimensionChanged);
    }

    // This hook fires only on entering the Nether, never on Overworld or End arrival.
    private void onDimensionChanged(PlayerEvent.PlayerChangedDimensionEvent event) {
        if (event.getTo() == Level.NETHER && event.getEntity() instanceof ServerPlayer player) {
            player.teleportTo(SPAWN_X, SPAWN_Y, SPAWN_Z);
        }
    }
}

package com.barttolo.ringworldnether.mixin;

import com.barttolo.ringworldnether.RingWorldNetherMod;
import dev.ringworld.platform.forge1201.Forge1201DimensionProfiles;
import dev.ringworld.world.RingGeometry;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Overrides Nether geometry only; does not override Overworld or End geometry. */
@Mixin(value = Forge1201DimensionProfiles.class, remap = false)
public abstract class NetherDimensionProfileMixin {
    @Inject(method = "bootstrapGeometry", at = @At("HEAD"), cancellable = true, remap = false)
    private static void netherBootstrap(ServerLevel level, CallbackInfoReturnable<RingGeometry> ci) {
        if (level.dimension() == Level.NETHER) {
            ci.setReturnValue(new RingGeometry(RingWorldNetherMod.NETHER_WIDTH, RingWorldNetherMod.NETHER_CIRCUMFERENCE));
        }
    }

    @Inject(method = "fixedGeometry", at = @At("HEAD"), cancellable = true, remap = false)
    private static void netherFixed(ServerLevel level, CallbackInfoReturnable<RingGeometry> ci) {
        if (level.dimension() == Level.NETHER) {
            ci.setReturnValue(new RingGeometry(RingWorldNetherMod.NETHER_WIDTH, RingWorldNetherMod.NETHER_CIRCUMFERENCE));
        }
    }
}

package com.barttolo.ringworldnether.mixin;

import com.barttolo.ringworldnether.RingWorldNetherMod;
import dev.ringworld.platform.forge1201.Forge1201GeneratorAccess;
import dev.ringworld.platform.forge1201.Forge1201RingRuntime;
import dev.ringworld.world.RingGeometry;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Limit only the Nether rim to 40 blocks; leave other dimension settings alone. */
@Mixin(value = Forge1201RingRuntime.class, remap = false)
public abstract class NetherRuntimeWallMixin {
    @Inject(method = "attach", at = @At("RETURN"), remap = false)
    private static void wallAtNetherAttach(ServerLevel level, CallbackInfoReturnable<RingGeometry> ci) {
        if (level.dimension() != Level.NETHER) return;
        if (level.getChunkSource().getGenerator() instanceof Forge1201GeneratorAccess access) {
            access.ringworld1201$setWallHeight(RingWorldNetherMod.NETHER_WALL_HEIGHT);
        }
    }
}

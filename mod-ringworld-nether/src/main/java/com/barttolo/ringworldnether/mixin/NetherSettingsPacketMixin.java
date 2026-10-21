package com.barttolo.ringworldnether.mixin;

import com.barttolo.ringworldnether.RingWorldNetherMod;
import dev.ringworld.platform.forge1201.Forge1201RingNetwork;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArgs;
import org.spongepowered.asm.mixin.injection.invoke.arg.Args;

/** Only adjusts fields #2 and #3 (Nether width/circumference) of the settings packet.
 * Fields #0/#1 (Overworld) and #4/#5 (End) retain their original values.
 */
@Mixin(value = Forge1201RingNetwork.class, remap = false)
public abstract class NetherSettingsPacketMixin {
    @ModifyArgs(method = "sendSettings", remap = false,
        at = @At(value = "INVOKE", remap = false,
            target = "Ldev/ringworld/platform/forge1201/Forge1201SettingsPacket;<init>(IIIIIIJIIIIJ)V"))
    private static void netherDimensionsInPacket(Args args) {
        args.set(2, RingWorldNetherMod.NETHER_WIDTH);
        args.set(3, RingWorldNetherMod.NETHER_CIRCUMFERENCE);
    }
}

"""Exercise the actual SDL helper extracted from the patched source, without Android hardware."""
from pathlib import Path
import subprocess
import sys
import tempfile

source = Path(sys.argv[1]).read_text()
start = source.index('static int uae4arm_pad_directions')
end = source.index('JNIEXPORT jint JNICALL', start)
helper = source[start:end]
stub = r'''
#include <assert.h>
#include <math.h>
typedef int SDL_scancode;
#define SDL_ANDROID_MAX_GAMEPADS 4
#define JOY_GAMEPAD1 2
#define SDL_PRESSED 1
#define SDL_RELEASED 0
#define SDL_KEY(x) K_##x
#define NORMALIZE_FLOAT_32767(x) ((int)(fminf(32767.0f, fmaxf(-32767.0f, (x)*32767.0f))))
enum {KEYCODE_BUTTON_A=96,KEYCODE_BUTTON_MODE=110,KEYCODE_BUTTON_1=188,KEYCODE_BUTTON_4=191,KEYCODE_BUTTON_16=203};
enum {K_PAGEUP=280,K_PAGEDOWN,K_END,K_HOME,K_F13,K_RCTRL,K_LALT,K_UP,K_DOWN,K_LEFT,K_RIGHT,K_F12};
static void *SDL_ANDROID_CurrentJoysticks[6] = {0,0,(void*)1,(void*)1,0,0};
static int buttons[6][7];
static int axes[6][2];
static void SDL_ANDROID_MainThreadPushJoystickButton(int pad,int button,int state) {buttons[pad][button]=state;}
static void SDL_ANDROID_MainThreadPushJoystickAxis(int pad,int axis,int state) {axes[pad][axis]=state;}
'''
checks = r'''
int main(void) {
    /* The user's button 4, on both controllers, is Fire. Release is independent. */
    assert(uae4arm_pad_key(KEYCODE_BUTTON_4, 0, 1, 1));
    assert(buttons[2][0] == 1 && buttons[3][0] == 0);
    assert(uae4arm_pad_key(KEYCODE_BUTTON_4, 0, 1, 2));
    assert(buttons[2][0] == 1 && buttons[3][0] == 1);
    uae4arm_pad_key(KEYCODE_BUTTON_4, 0, 0, 1);
    assert(buttons[2][0] == 0 && buttons[3][0] == 1);
    uae4arm_pad_key(KEYCODE_BUTTON_4, 0, 0, 2);
    assert(buttons[2][0] == 0 && buttons[3][0] == 0);
    /* A controller translated to screen button 4 also becomes Fire. */
    assert(uae4arm_pad_key(KEYCODE_BUTTON_A, K_PAGEUP, 1, 2));
    assert(buttons[3][0] == 1);
    uae4arm_pad_key(KEYCODE_BUTTON_A, K_PAGEUP, 0, 2);
    /* Real keyboard PageUp and emulator shortcuts retain their previous path. */
    assert(!uae4arm_pad_key(92, K_PAGEUP, 1, 0));
    assert(!uae4arm_pad_key(82, K_F12, 1, 1));
    /* Both controllers steer independently, including simultaneous opposing inputs. */
    assert(uae4arm_pad_key(21, K_LEFT, 1, 1));
    assert(uae4arm_pad_key(22, K_RIGHT, 1, 2));
    assert(axes[2][0] == -32767 && axes[3][0] == 32767);
    uae4arm_pad_key(21, K_LEFT, 0, 1);
    assert(axes[2][0] == 0 && axes[3][0] == 32767);
    uae4arm_pad_key(22, K_RIGHT, 0, 2);
    assert(axes[3][0] == 0);
    /* Releasing the digital d-pad restores the analog stick, per controller. */
    uae4arm_pad_analog[0][0] = 0.75f;
    uae4arm_pad_analog[1][1] = -0.5f;
    uae4arm_pad_axes(0); uae4arm_pad_axes(1);
    assert(axes[2][0] > 24000 && axes[3][1] < -16000);
    /* Unknown/unopened gamepads fall back without touching either active player. */
    assert(!uae4arm_pad_key(KEYCODE_BUTTON_4, 0, 1, 3));
    assert(!uae4arm_pad_key(KEYCODE_BUTTON_4, 0, 1, 9));
    return 0;
}
'''
with tempfile.TemporaryDirectory() as tmp:
    c = Path(tmp)/'test.c'
    exe = Path(tmp)/'test'
    c.write_text(stub + helper + checks)
    subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', str(c), '-lm', '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
print('PASS: controller button 4, releases, two-player isolation, directions, analog fallback, and keyboard preservation')

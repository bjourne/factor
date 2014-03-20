#include "master.hpp"

int my_argc;
wchar_t** my_argv;

DWORD WINAPI wmain_thread(LPVOID lpParam) {
  factor::init_globals();
  factor::start_standalone_factor(my_argc, my_argv);
  return 0;
}

VM_C_API int wmain(int argc, wchar_t** argv) {
  // printf("wmain\n");
  my_argc = argc;
  my_argv = argv;
  factor::boot_thread = CreateThread(NULL, 0, wmain_thread, NULL, 0, NULL);
  // printf("wmain: boot_thread = %d\n", factor::boot_thread);
  WaitForSingleObject(factor::boot_thread, INFINITE);

  // printf("infinite wait is over\n");

  // return 0;
  // factor::init_globals();
  // factor::start_standalone_factor(argc, argv);
  return 0;
}

// HANDLE boot_thread;

// DWORD WINAPI wmain_threaded(LPVOID lpParam) {
//   printf("wmain_threaded tid = %d\n", GetCurrentThread());
//   int argc;
//   wchar_t** argv = CommandLineToArgvW(GetCommandLine(), &argc);
//   wmain(argc, argv);

//   return 0;
// }


int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance,
                   LPSTR lpCmdLine, int nCmdShow) {

  printf("WinMain tid = %d\n", GetCurrentThread());
  // factor::boot_thread = (HANDLE)88;
  // factor::boot_thread = CreateThread(NULL, 0, wmain_threaded, NULL, 0, NULL);
  // factor::boot_thread = (HANDLE)33;
  // printf("boot_thread = %d\n", factor::boot_thread);
  // WaitForSingleObject(factor::boot_thread, INFINITE);
  // return 0;

  // int argc;
  // wchar_t** argv = CommandLineToArgvW(GetCommandLine(), &argc);
  // wmain(argc, argv);

  // return 0;
}

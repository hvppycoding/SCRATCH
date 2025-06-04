#!/usr/bin/env python3
import subprocess

def get_input(prompt, default, cast_func=str, allow_zero=False):
    while True:
        val = input(f"{prompt} [{default}]: ").strip()
        if not val:
            return default
        try:
            value = cast_func(val)
            if not allow_zero and cast_func == int and value <= 0:
                print("0보다 큰 숫자를 입력하거나 Enter를 눌러 기본값을 사용하세요.")
                continue
            return value
        except ValueError:
            print("잘못된 입력입니다. 다시 시도하세요.")

def main():
    print("=== bsub 실행 도우미 ===")

    num_cores = get_input("사용할 코어 수", 1, int)
    mem_gb = get_input("요청 메모리 (GB)", 8, int)
    timeout_hours = get_input("제한 시간 (시간, 0이면 무제한)", 8, int, allow_zero=True)
    command = input("실행할 커맨드 [xterm]: ").strip() or "xterm"

    mem_str = f"{mem_gb}GB"
    time_str = "" if timeout_hours == 0 else f"-W {timeout_hours}:00"

    bsub_cmd = f"bsub -n {num_cores} -R 'rusage[mem={mem_gb*1024}]' {time_str} {command}"
    print(f"\n실행할 bsub 명령어:\n{bsub_cmd}")

    confirm = input("\n실행할까요? [Y/n]: ").strip().lower()
    if confirm in ["", "y", "yes"]:
        subprocess.run(bsub_cmd, shell=True)
    else:
        print("실행을 취소했습니다.")

if __name__ == "__main__":
    main()

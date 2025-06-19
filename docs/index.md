# Descrição
Uma Lib para automatizar sistemas maiframe com python.
Fornece ferramentas para automatização, gravação e reprodução de sistemas mainframe.

## :bookmark_tabs: Comandos

* `pyx3270 record [address] [directory] [tls] [model] [emulator]` - Inicia a gravação das telas do terminal e salva os bytes no diretorio.
* `pyx3270 replay [directory] [port] [tls] [model] [emulator]` - Inicia a reprodução das telas gravadas e armazanadas anteriormente em modo offline.


## :open_file_folder: Layout do Projeto

```
├───pyx3270
│   │   command_config.py
│   │   emulator.py
│   │   exceptions.py
│   │   iemulator.py
│   │   server.py
│   │   tn3270.py
│   │   __init__.py
│   └───__main__.py
└───screens
```

## :jigsaw: Diagrama de Classes

``` mermaid
classDiagram
    %% Interfaces
    class AbstractExecutableApp {
        <<interface>>
        +connect(*args)
        +close()
        +write(data)
        +readline()
        -_spawn_app()
        -_get_executable_app_args(model)
    }

    class AbstractCommand {
        <<interface>>
        +execute()
        +handle_result(result)
    }

    class AbstractEmulatorCmd {
        <<interface>>
        +clear_screen()
        +wait_for_field(timeout)
        +wait_string_found(ypos, xpos, string, equal, timeout)
        +string_found(ypos, xpos, string)
        +delete_field()
        +move_to(ypos, xpos)
        +send_pf(value)
        +send_string(tosend, ypos, xpos)
        +send_enter(times)
        +send_home()
        +get_string()
        +get_string_area(yposi, xposi, ypose, xpose)
        +get_full_screen(header)
        +save_screen(file_path, file_name)
        +search_string(string, ignore_case)
        +get_string_positions(string, ignore_case)
        -_get_ypos_and_xpos_from_index(index)
    }

    class AbstractEmulator {
        <<interface>>
        +terminate()
        +is_connected()
        +connect_host(host, port, tls)
        +reconnect_host()
        -_create_app()
        -_exec_command(cmdstr)
    }

    %% Implementações
    class ExecutableApp {
        +shell: bool
        +subprocess
        +args
        +connect(*args)
        +close()
        +write(data)
        +readline()
        -_spawn_app()
        -_get_executable_app_args(model)
    }

    class Wc3270App {
        +script_port
        +socket
        +socket_fh
        +connect(host)
        +close()
        +write(data)
        +readline()
        -_make_socket()
        -_get_free_port()
    }

    class Ws3270App {
        +args
    }

    class X3270App {
        +args
    }
    
    class S3270App{
        +args
    }

    class Command {
        +app: ExecutableApp
        +cmdstr: bytes
        +status_line
        +data
        +execute()
        +handle_result(result)
    }

    class X3270Cmd {
        +clear_screen()
        +wait_for_field(timeout)
        +wait_string_found(ypos, xpos, string, equal, timeout)
        +string_found(ypos, xpos, string)
        +delete_field()
        +move_to(ypos, xpos)
        +send_pf(value)
        +send_string(tosend, ypos, xpos)
        +send_enter(times)
        +send_home()
        +get_string()
        +get_string_area(yposi, xposi, ypose, xpose)
        +get_full_screen(header)
        +save_screen(file_path, file_name)
        +search_string(string, ignore_case)
        +get_string_positions(string, ignore_case)
        -_get_ypos_and_xpos_from_index(index)
    }

    class X3270 {
        +model: str 
        +model_dimensions: dict
        +visible: bool
        +app: ExecutableApp
        +is_terminated: bool
        +host: str
        +port: int
        +tls: bool
        +terminate()
        +is_connected()
        +connect_host(host, port, tls)
        +reconnect_host()
        -_create_app()
        -_exec_command(cmdstr)
    }

    %% Relações
    X3270 --|> AbstractEmulator
    X3270 --|> X3270Cmd
    ExecutableApp ..|> AbstractExecutableApp
    Wc3270App --|> ExecutableApp
    Ws3270App --|> ExecutableApp
    X3270App --|> ExecutableApp
    S3270App --|> ExecutableApp
    Command ..|> AbstractCommand
    X3270Cmd ..|> AbstractEmulatorCmd

```

## :clock2: Changelogs

:: towncrier-draft Unreleased changes

--8<-- "CHANGELOG.md"
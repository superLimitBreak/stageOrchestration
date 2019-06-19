from _main import main

def _main(**kwargs):
    from stageOrchestration import server
    server.serve(**kwargs)

if __name__ == "__main__":
    main(_main)

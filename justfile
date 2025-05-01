_default:
    just --list

dev-server:
    uv run uvicorn api.main:app --reload --host 0.0.0.0

landing-page:
    zola serve -i 0.0.0.0 --base-url /

build-css:
    bunx unocss templates/*.html -o static/css/uno.css
    

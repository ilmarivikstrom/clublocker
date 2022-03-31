mkdir -p ~/.streamlit/

echo "\
[theme]\n\
primaryColor=\"#E3001A\"\n\
backgroundColor=\"#1E1F22\"\n\
secondaryBackgroundColor=\"#323232\"\n\
base=\"dark\"\n\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
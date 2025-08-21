document.addEventListener("DOMContentLoaded", () => {
    const terminals = document.querySelectorAll(".termynal");
    terminals.forEach(el => new Termynal(el));
});


function copyText(text, button) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            button.textContent = "✅ Copiado!";
            setTimeout(() => button.textContent = "📋 Copiar", 2000);
        }).catch(err => {
            console.error("Erro ao copiar:", err);
        });
    } else {
        // Fallback para ambientes sem HTTPS
        const textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.style.position = "fixed"; // Evita rolagem
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();

        try {
            document.execCommand("copy");
            button.textContent = "✅ Copiado!";
            setTimeout(() => button.textContent = "📋 Copiar", 2000);
        } catch (err) {
            console.error("Fallback falhou:", err);
        }

        document.body.removeChild(textarea);
    }
}

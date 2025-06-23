document.addEventListener("DOMContentLoaded", function () {
    // --- Lógica de Transição Login/Cadastro ---
    const btnSignin = document.querySelector("#signin");
    const btnSignup = document.querySelector("#signup");
    const body = document.querySelector("body");

    if (btnSignin && body) {
        btnSignin.addEventListener("click", function () {
            body.className = "sign-in-js";
        });
    }

    if (btnSignup && body) {
        btnSignup.addEventListener("click", function () {
            body.className = "sign-up-js";
        });
    }

    // Ativa o painel de login/sign-in se houver um erro de login do servidor
    // A classe `error-login` é adicionada pelo Jinja no parágrafo de erro.
    const errorLoginMessage = document.querySelector('.error-message-server.error-login');
    if (errorLoginMessage && body) {
        body.classList.add('sign-in-js');
    }

    // --- Lógica de Validação de Formulário de Cadastro ---
    const btnEnviar = document.getElementById('btn-enviar');
    if (btnEnviar) {
        btnEnviar.addEventListener('click', function (event) {
            event.preventDefault(); // Impede o envio padrão do formulário

            clearErrors(); // Limpa mensagens de erro anteriores

            // Validações
            const nomeValido = validarNome();
            const sobrenomeValido = validarSobrenome();
            // const generoValido = validarGenero(); // Descomente se 'genero-cadastro' for usado
            const cpfValido = validarCPF();
            const dataNascimentoValida = validarDataNascimento();
            const telefoneValido = validarTelefone();
            const senhaValida = validarSenha();
            const emailValido = validarEmail();

            // Envia o formulário apenas se todas as validações passarem
            if (nomeValido && sobrenomeValido && cpfValido &&
                dataNascimentoValida && telefoneValido && senhaValida && emailValido) {
                document.getElementById('cadastroForm').submit();
            }
        });
    }

    // --- Event Listeners para Validação e Formatação em Tempo Real ---
    const nomeInput = document.getElementById('nome-cadastro');
    if (nomeInput) nomeInput.addEventListener('input', validarNome);

    const sobrenomeInput = document.getElementById('sobrenome-cadastro');
    if (sobrenomeInput) sobrenomeInput.addEventListener('input', validarSobrenome);

    const nascimentoInput = document.getElementById('nascimento-cadastro');
    if (nascimentoInput) nascimentoInput.addEventListener('blur', validarDataNascimento);

    const emailInput = document.getElementById('email-cadastro');
    if (emailInput) emailInput.addEventListener('blur', validarEmail);

    const cpfInput = document.getElementById('cpf-cadastro');
    if (cpfInput) {
        cpfInput.addEventListener('input', function() { formatarCPF(this); validarCPF(); });
        cpfInput.addEventListener('blur', validarCPF);
    }

    const telefoneInput = document.getElementById('telefone-cadastro');
    if (telefoneInput) {
        telefoneInput.addEventListener('input', function() { formatarTelefone(this); validarTelefone(); });
        telefoneInput.addEventListener('blur', validarTelefone);
    }

    const senhaInput = document.getElementById('senha-cadastro');
    const confirmarSenhaInput = document.getElementById('confirmar-senha-cadastro');
    if (senhaInput && confirmarSenhaInput) {
        senhaInput.addEventListener('input', validarSenha);
        confirmarSenhaInput.addEventListener('input', validarSenha);
    }

    // --- Lógica de Modais ---
    const openPasswordModalBtn = document.getElementById("openModal");
    if (openPasswordModalBtn) {
        openPasswordModalBtn.addEventListener("click", function(event) {
            openModal("forgotPasswordModal", event);
        });
    }

    const closeForgotPasswordModalBtn = document.getElementById("closeForgotPasswordModal");
    if (closeForgotPasswordModalBtn) {
        closeForgotPasswordModalBtn.addEventListener("click", function() {
            closeModal("forgotPasswordModal");
        });
    }

    window.addEventListener("click", function(event) {
        const modal = document.getElementById("forgotPasswordModal");
        if (modal && event.target === modal) {
            closeModal("forgotPasswordModal");
        }
    });

    // --- Funções de Validação e Utilidade ---

    function validarNome() {
        const input = document.getElementById('nome-cadastro');
        if (!input) return true;
        const value = input.value.trim();
        if (value === '') { showError('nomeError', 'O nome é obrigatório.', input); return false; }
        if (value.length < 3) { showError('nomeError', 'O nome deve ter no mínimo 3 caracteres.', input); return false; }
        removeError(input, 'nomeError');
        return true;
    }

    function validarSobrenome() {
        const input = document.getElementById('sobrenome-cadastro');
        if (!input) return true;
        const value = input.value.trim();
        if (value === '') { showError('sobrenomeError', 'O sobrenome é obrigatório.', input); return false; }
        if (value.length < 3) { showError('sobrenomeError', 'O sobrenome deve ter no mínimo 3 caracteres.', input); return false; }
        removeError(input, 'sobrenomeError');
        return true;
    }

    // function validarGenero() { // Descomente e ajuste se necessário
    //     const select = document.getElementById('genero-cadastro');
    //     if (!select) return true;
    //     const value = select.value;
    //     if (value === "" || value === null) { showError('generoError', 'Por favor, selecione um gênero.', select); return false; }
    //     removeError(select, 'generoError');
    //     return true;
    // }

    function validarCPF() {
        const input = document.getElementById('cpf-cadastro');
        if (!input) return true;
        const cpf = input.value.trim();
        const strCPF = String(cpf).replace(/[^\d]/g, '');
        if (strCPF.length !== 11) { showError('cpfError', 'CPF inválido. Deve conter 11 dígitos.', input); return false; }
        const cpfsInvalidos = ['00000000000', '11111111111', '22222222222', '33333333333', '44444444444', '55555555555', '66666666666', '77777777777', '88888888888', '99999999999'];
        if (cpfsInvalidos.includes(strCPF)) { showError('cpfError', 'CPF inválido.', input); return false; }
        let soma = 0;
        for (let i = 1; i <= 9; i++) { soma += parseInt(strCPF.substring(i - 1, i)) * (11 - i); }
        let resto = (soma * 10) % 11;
        if (resto === 10 || resto === 11) resto = 0;
        if (resto !== parseInt(strCPF.substring(9, 10))) { showError('cpfError', 'CPF inválido.', input); return false; }
        soma = 0;
        for (let i = 1; i <= 10; i++) { soma += parseInt(strCPF.substring(i - 1, i)) * (12 - i); }
        resto = (soma * 10) % 11;
        if (resto === 10 || resto === 11) resto = 0;
        if (resto !== parseInt(strCPF.substring(10, 11))) { showError('cpfError', 'CPF inválido.', input); return false; }
        removeError(input, 'cpfError');
        return true;
    }

    function validarDataNascimento() {
        const input = document.getElementById('nascimento-cadastro');
        if (!input) return true;
        const dataNascimento = input.value;
        const hoje = new Date();
        const dataNasc = new Date(dataNascimento + 'T00:00:00'); // Adiciona T00:00:00 para evitar problemas de fuso horário
        if (dataNascimento === '') { showError('dataNascimentoError', 'A data de nascimento é obrigatória.', input); return false; }
        if (dataNasc > hoje) { showError('dataNascimentoError', 'Por favor, digite uma data de nascimento válida.', input); return false; }
        removeError(input, 'dataNascimentoError');
        return true;
    }

    function validarEmail() {
        const input = document.getElementById('email-cadastro');
        if (!input) return true;
        const email = input.value.trim();
        const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (email === '') { showError('emailError', 'O e-mail é obrigatório.', input); return false; }
        if (!regexEmail.test(email)) { showError('emailError', 'Por favor, insira um e-mail válido.', input); return false; }
        removeError(input, 'emailError');
        return true;
    }

    function validarTelefone() {
        const input = document.getElementById('telefone-cadastro');
        if (!input) return true;
        const telefone = input.value.trim();
        const apenasNumeros = telefone.replace(/\D/g, '');
        if (telefone === '') { showError('telefoneError', 'O telefone é obrigatório.', input); return false; }
        if (apenasNumeros.length < 10 || apenasNumeros.length > 11) { showError('telefoneError', 'Número inválido. Use (XX) XXXX-XXXX ou (XX) 9XXXX-XXXX.', input); return false; }
        const ddd = apenasNumeros.substring(0, 2);
        if (ddd < 11 || ddd > 99 || [20, 23, 25, 26, 29, 30, 36, 39, 40, 50, 52, 56, 57, 58, 59, 60, 70, 72, 76, 77, 78, 80].includes(parseInt(ddd))) {
            showError('telefoneError', 'DDD inválido.', input); return false;
        }
        removeError(input, 'telefoneError');
        return true;
    }

    function validarSenha() {
        const senhaInput = document.getElementById("senha-cadastro");
        const confirmarSenhaInput = document.getElementById("confirmar-senha-cadastro");
        if (!senhaInput || !confirmarSenhaInput) return true;

        const senha = senhaInput.value;
        const confirmarSenha = confirmarSenhaInput.value;

        // Mínimo 8 caracteres, 1 maiúscula, 1 minúscula, 1 número e 1 especial
        const regexSenhaSegura = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

        if (senha.length < 8) {
            showError('senhaError', 'A senha deve ter no mínimo 8 caracteres', senhaInput);
            return false;
        } else if (!regexSenhaSegura.test(senha)) {
            showError('senhaError', 'A senha deve conter: 1 letra maiúscula, 1 minúscula, 1 número e 1 caractere especial (@$!%*?&)', senhaInput);
            return false;
        } else {
            removeError(senhaInput, 'senhaError');
        }

        if (senha !== confirmarSenha) {
            showError('confirmarSenhaError', 'As senhas não coincidem', confirmarSenhaInput);
            return false;
        } else {
            removeError(confirmarSenhaInput, 'confirmarSenhaError');
        }

        return true;
    }

    // A função validaImagem e lógica de preview de imagem geralmente não pertencem à página de login/cadastro
    // a menos que haja um upload de foto de perfil durante o cadastro.
    // Se for o caso, pode mantê-la aqui, senão pode ser removida.
    // function validaImagem(input) { ... }

    // Helper para exibir mensagens de erro
    function showError(id, message, inputElement = null) {
        const errorElement = document.getElementById(id);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
            if (inputElement) {
                inputElement.classList.add('invalid');
                inputElement.classList.remove('valid');
            }
        }
    }

    // Helper para remover mensagens de erro e classes
    function removeError(inputElement, errorId) {
        const errorElement = document.getElementById(errorId);
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.style.display = 'none';
        }
        if (inputElement) {
            inputElement.classList.remove('invalid');
            inputElement.classList.add('valid');
        }
    }

    // Limpa todos os erros de uma vez
    function clearErrors() {
        document.querySelectorAll('.error-message').forEach(error => {
            error.textContent = '';
            error.style.display = 'none';
        });
        document.querySelectorAll('input, select').forEach(input => {
            input.classList.remove('invalid');
            input.classList.remove('valid');
        });
    }

    function formatarTelefone(campo) {
        const posicaoCursor = campo.selectionStart;
        let valor = campo.value.replace(/\D/g, '');
        valor = valor.substring(0, 11);
        let formato = '';
        if (valor.length > 0) { formato = `(${valor.substring(0, 2)}`; }
        if (valor.length > 2) { formato += `) ${valor.substring(2, 7)}`; }
        if (valor.length > 7) { formato += `-${valor.substring(7, 11)}`; }
        campo.value = formato;
        if (posicaoCursor === 1 && valor.length > 2) { campo.setSelectionRange(4, 4); }
        else if (posicaoCursor === 4 && valor.length > 7) { campo.setSelectionRange(10, 10); }
    }

    function formatarCPF(input) {
        let num = input.value.replace(/\D/g, "");
        if (num.length > 11) num = num.substring(0, 11);
        let formatado = "";
        if (num.length > 3) {
            formatado = num.substring(0, 3) + ".";
            if (num.length > 6) {
                formatado += num.substring(3, 6) + ".";
                if (num.length > 9) {
                    formatado += num.substring(6, 9) + "-";
                    formatado += num.substring(9, 11);
                } else {
                    formatado += num.substring(6);
                }
            } else {
                formatado += num.substring(3);
            }
        } else {
            formatado = num;
        }
        input.value = formatado;
    }

    // Função para abrir o modal
    function openModal(modalId, event) {
        if (event) event.preventDefault();
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = "block";
        }
    }

    // Função para fechar o modal
    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = "none";
        }
    }
});
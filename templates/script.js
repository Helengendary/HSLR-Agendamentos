document.getElementById('cadastroForm').addEventListener('submit', function (event) {
    event.preventDefault(); //impede o envio do formulário se n houver nada preenchido

    //limpa mensagens de erro anteriores
    clearErrors();

    //validações
    const nomeValido = validarNome();
    const sobrenomeValido = validarSobrenome();
    const cpfValido = validarCPF();
    const dataNascimentoValida = validarDataNascimento();
    const telefoneValido = validarTelefone();
    const senhaValida = validarSenha();

    //vai permitir o envio apenas se todas as validações passarem
    // if (nomeValido && sobrenomeValido && cpfValido 
    //     && dataNascimentoValida && telefoneValido && senhaValida) {
    //     // alert('Formulário enviado com sucesso!');
    //     //implementar o envio para o BACKEND
    // }
});

function validarNome() {
    const nome = document.getElementById('nome-cadastro').value.trim();
    if (nome === '') {
        showError('nomeError', 'O nome é obrigatório.');
        return false;
    } else if (nome.length < 3) {
        showError('nomeError', 'O nome deve ter no mínimo 3 caracteres.');
        return false;
    }
    return true;
}

function validarSobrenome() {
    const sobrenome = document.getElementById('sobrenome-cadastro').value.trim();
    if (sobrenome === '') {
        showError('sobrenomeError', 'O sobrenome é obrigatório.');
        return false;
    }
    return true;
}

function validarCPF() {
    const cpf = document.getElementById('cpf-cadastro').value.trim();
    const strCPF = String(cpf).replace(/[^\d]/g, ''); //vai remover caracteres não numéricos

    if (strCPF.length !== 11) {
        showError('cpfError', 'CPF inválido. Deve conter 11 dígitos.');
        return false;
    }

    //vai verificar CPFs inválidos
    const cpfsInvalidos = [
        '00000000000', '11111111111', '22222222222', '33333333333',
        '44444444444', '55555555555', '66666666666', '77777777777',
        '88888888888', '99999999999'
    ];
    if (cpfsInvalidos.includes(strCPF)) {
        showError('cpfError', 'CPF inválido.');
        return false;
    }

    //validação do CPF (cálculo dos dígitos verificadores)
    let soma = 0;
    for (let i = 1; i <= 9; i++) {
        soma += parseInt(strCPF.substring(i - 1, i)) * (11 - i);
    }
    let resto = (soma * 10) % 11;
    if (resto === 10 || resto === 11) resto = 0;
    if (resto !== parseInt(strCPF.substring(9, 10))) {
        showError('cpfError', 'CPF inválido.');
        return false;
    }

    soma = 0;
    for (let i = 1; i <= 10; i++) {
        soma += parseInt(strCPF.substring(i - 1, i)) * (12 - i);
    }
    resto = (soma * 10) % 11;
    if (resto === 10 || resto === 11) resto = 0;
    if (resto !== parseInt(strCPF.substring(10, 11))) {
        showError('cpfError', 'CPF inválido.');
        return false;
    }

    return true;
}

function validarDataNascimento() {
    const dataNascimento = document.getElementById('nascimento-cadastro').value;
    const hoje = new Date();
    const dataNasc = new Date(dataNascimento);

    if (dataNascimento === '') {
        showError('dataNascimentoError', 'A data de nascimento é obrigatória.');
        return false;
    } else if (dataNasc > hoje) {
        showError('dataNascimentoError', 'Por favor, digite uma data de nascimento válida.');
        return false;
    }
    return true;
}

function validarTelefone() {
    const telefone = document.getElementById('telefone-cadastro').value.trim();
    const regexTelefone = /^\(\d{2}\) \d{5}-\d{4}$/; // Formato (XX) XXXXX-XXXX

    if (telefone === '') {
        showError('telefoneError', 'O telefone é obrigatório.');
        return false;
    } else if (!regexTelefone.test(telefone)) {
        showError('telefoneError', 'Telefone inválido. Use o formato (XX) XXXXX-XXXX.');
        return false;
    }
    return true;
}

function mostrarOcultarSenhaCadastro() {
    var senha = document.getElementById("Senha");
    var confirmarSenha = document.getElementById("ConfirmarSenha");
  
    if (senha.type == "password"){
      confirmarSenha.type = "text";
      confirmarSenha.type = "text";
    } else {
      senha.type = "password";
      senha.type = "password";
    }
  }
  
  //validar senha 
  function validarSenha() {
    var senha  = document.getElementById("senha-cadastro").value;
    var confirmarSenha = document.getElementById("confimar-senha-cadastro").value;
    
     //verifica se a senha é segura
    if (senha.length < 8) {
        alert("A senha deve ter pelo menos 8 caracteres!");
        return false; //retorna falso se n tiver pelo menos 8 caracteres
    }

    if (!/[A-Z]/.test(senha)) {
        alert("A senha deve conter pelo menos uma letra maiúscula!");
        return false; //retorna falso se n tiver pelo menos 1 maiuscula
    }

    if (!/[a-z]/.test(senha)) {
        alert("A senha deve conter pelo menos uma letra minúscula!");
        return false; //retorna falso se n tiver pelo menos 1 minuscula
    }

    if (!/[0-9]/.test(senha)) { 
        alert("A senha deve conter pelo menos um número!");
        return false; //retorna falso se n tiver pelo menos 1 número
    }

    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(senha)) {
        alert("A senha deve conter pelo menos um caractere especial!");
        return false; //retorna falso se n tiver pelo menos 1 caracter especial
    }

    //ve se a senha e confirmar senha possuem valores iguais
    if (senha != confirmarSenha) {
        confirmarSenha.setCustomValidity("Senhas diferentes!");
        confirmarSenha.reportValidity();
        return false; //retorna falso se tiver diferente
    }

    return true; //se a senha for segura, vai retornar true. 
  }
  
//mostra onde tem erro para o usuário
function showError(id, message) {
    const errorElement = document.getElementById(id);
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

function clearErrors() {
     //vai seleiconar todos os elementos com a classe 'error-message'
    const errors = document.querySelectorAll('.error-message');
    errors.forEach(error => {
        //limpa o texto do elemento de erro
        error.textContent = '';
        //define o display como 'none'
        error.style.display = 'none';
    });
}

function formatarTel(campo) {
    let num = campo.value.replace(/\D/g, ""); // Remove tudo que não for número

    if (num.length > 2) {
        num = `(${num.substring(0, 2)}) ${num.substring(2)}`;
    }
    if (num.length > 10) {
        num = `${num.substring(0, 10)}-${num.substring(10, 14)}`;
    }

    campo.value = num;
}

function formatarCPF(input) {
    let num = input.value.replace(/\D/g, ""); // Remove tudo que não for número

    if (num.length > 11) num = num.substring(0, 11); // Limita a 11 números

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
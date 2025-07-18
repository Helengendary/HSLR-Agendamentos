document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('btn-enviar').addEventListener('click', function (event) {
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
        const emailValido = validarEmail();

        // vai permitir o envio apenas se todas as validações passarem
        if (nomeValido && sobrenomeValido && cpfValido 
            && dataNascimentoValida && telefoneValido && senhaValida && emailValido ) {
                document.getElementById('cadastroForm').submit();
        }
    });
});

// valida nome
function validarNome() {
    const nome = document.getElementById('nome-cadastro').value.trim();
    if (nome === '') {
        showError('nomeError', 'O nome é obrigatório.');
        return false;
    } else if (nome.length < 3) {
        showError('nomeError', 'O nome deve ter no mínimo 3 caracteres.');
        return false;
    }return true;
}

// valida sobrenome
function validarSobrenome() {
    const sobrenome = document.getElementById('sobrenome-cadastro').value.trim();
    if (sobrenome === '') {
        showError('sobrenomeError', 'O sobrenome é obrigatório.');
        return false;
    } else if (sobrenome.length < 3) {
        showError('nomeError', 'O nome deve ter no mínimo 3 caracteres.');
        return false;
    }   return true;
}

// valida genero
function validarGenero() {
    const genero = document.getElementById('genero-cadastro').value;
    if (genero === "" || genero === null) {
        showError('generoError', 'Por favor, selecione um gênero.');
        return false;
    }
    return true;
}

// valida cpf
function validarCPF() {
    const cpf = document.getElementById('cpf-cadastro').value.trim();
    const strCPF = String(cpf).replace(/[^\d]/g, '');
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
        return false;}
soma = 0;
    for (let i = 1; i <= 10; i++) {
        soma += parseInt(strCPF.substring(i - 1, i)) * (12 - i);}
    resto = (soma * 10) % 11;
    if (resto === 10 || resto === 11) resto = 0;
    if (resto !== parseInt(strCPF.substring(10, 11))) {
        showError('cpfError', 'CPF inválido.');
        return false; }
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
        return false; }
    return true;
}

// validar email
function validarEmail() {
    const emailInput = document.getElementById('email-cadastro')
    const email = emailInput.value.trim();
    const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email === '') {
        showError('emailError', 'O e-mail é obrigatório.');
        emailInput.classList.add("invalid");
        return false;
    } else if (!regexEmail.test(email)) {
        showError('emailError', 'Por favor, insira um e-mail válido.');
        emailInput.classList.add("invalid");
        return false;
    }

    emailInput.classList.remove('invalid');
    return true;
}

// valida telefone
function validarTelefone() {
    const telefoneInput = document.getElementById('telefone-cadastro');
    const telefone = telefoneInput.value.trim();
    const apenasNumeros = telefone.replace(/\D/g, '');

    if (telefone === '') {
        showError('telefoneError', 'O telefone é obrigatório.');
        telefoneInput.classList.add('invalid');
        return false;
    }
    if (apenasNumeros.length < 10 || apenasNumeros.length > 11) {
        showError('telefoneError', 'Número inválido. Use (XX) XXXX-XXXX ou (XX) 9XXXX-XXXX.');
        telefoneInput.classList.add('invalid');
        return false;
    }
    //vai verificar DDD válido (11-99, exceto alguns específicos)
    const ddd = apenasNumeros.substring(0, 2);
    if (ddd < 11 || ddd > 99 || [20, 23, 25, 26, 29, 30, 36, 39, 40, 50, 52, 56, 57, 58, 59, 60, 70, 72, 76, 77, 78, 80].includes(parseInt(ddd))) {
        showError('telefoneError', 'DDD inválido.');
        telefoneInput.classList.add('invalid');
        return false;
    }
    telefoneInput.classList.remove('invalid');
    document.getElementById('telefoneError').textContent = '';
    return true;
}

// mostra e oculta a senha
function mostrarOcultarSenhaCadastro() {
    var senha = document.getElementById("senha-cadastro");
    var confirmarSenha = document.getElementById("confirmar-senha-cadastro");
    if (senha.type === "password") {
        senha.type = "text";
        confirmarSenha.type = "text";
    } else {
        senha.type = "password";
        confirmarSenha.type = "password";}
}

// validar senha 
function validarSenha() {
    const senha = document.getElementById("senha-cadastro");
    const confirmarSenha = document.getElementById("confirmar-senha-cadastro");
    
    //regex melhorado (mínimo 8 chars, 1 maiúscula, 1 minúscula, 1 número e 1 especial)
    const regexSenhaSegura = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    
    //verificação completa
    if (senha.value.length < 8) {
        showError('senhaError', 'A senha deve ter no mínimo 8 caracteres');
        senha.classList.add("invalid");
        return false;
    } else if (!regexSenhaSegura.test(senha.value)) {
        showError('senhaError', 'A senha deve conter: 1 letra maiúscula, 1 minúscula, 1 número e 1 caractere especial (@$!%*?&)');
        senha.classList.add("invalid");
        return false;
    } else if (senha.value !== confirmarSenha.value) {
        showError('confirmarSenhaError', 'As senhas não coincidem');
        confirmarSenha.classList.add("invalid");
        return false;
    } else {
        senha.classList.remove("invalid");
        senha.classList.add("valid");
        confirmarSenha.classList.remove("invalid");
        confirmarSenha.classList.add("valid");
        document.getElementById('senhaError').textContent = "";
        document.getElementById('confirmarSenhaError').textContent = "";
        return true;
    }
}

//validar imagem perfil
function validaImagem(input) {
    var caminho = input.value;
  
    if (caminho) {
        var comecoCaminho = (caminho.indexOf('\\') >= 0 ? caminho.lastIndexOf('\\') : caminho.lastIndexOf('/'));
        var nomeArquivo = caminho.substring(comecoCaminho);
  
        if (nomeArquivo.indexOf('\\') === 0 || nomeArquivo.indexOf('/') === 0) {
            nomeArquivo = nomeArquivo.substring(1);
        }
  
        var extensaoArquivo = nomeArquivo.indexOf('.') < 1 ? '' : nomeArquivo.split('.').pop();
  
        if (extensaoArquivo != 'gif' &&
            extensaoArquivo != 'png' &&
            extensaoArquivo != 'jpg' &&
            extensaoArquivo != 'jpeg') {
            input.value = '';
            alert("É preciso selecionar um arquivo de imagem (gif, png, jpg ou jpeg)");
        }
    } else {
        input.value = '';
        alert("Selecione um caminho de arquivo válido");
    }
    if (input.files && input.files[0]) {
        var arquivoTam = input.files[0].size / 1024 / 1024;
        if (arquivoTam < 16) {
            var reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('imagemSelecionada').setAttribute('src', e.target.result);
            };
            reader.readAsDataURL(input.files[0]);
        } else {
            input.value = '';
            alert("O arquivo precisa ser uma imagem com menos de 16 MB");
        }
    } else{
        document.getElementById('imagemSelecionada').setAttribute('src', '#');
    }
}
  
// mostrar erro
function showError(id, message) {
    const errorElement = document.getElementById(id);
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    errorElement.style.color = '#ff0000';
    
    //adiciona classe invalid ao input correspondente
    const inputId = id.replace('Error', '-cadastro');
    const inputElement = document.getElementById(inputId);
    if (inputElement) {
        inputElement.classList.add('invalid');
    }
}

function clearErrors() {
    const errors = document.querySelectorAll('.error-message');
    errors.forEach(error => {
        error.textContent = '';
        error.style.display = 'none';
    });
    
    //remove classes invalid de todos os inputs
    document.querySelectorAll('input, select').forEach(input => {
        input.classList.remove('invalid');
    });
}
//vai formatar o telefone ao digitar
function formatarTelefone(campo) {
    // Pega posição atual do cursor
    const posicaoCursor = campo.selectionStart;
    let valor = campo.value.replace(/\D/g, '');
    
    // Limita a 11 caracteres
    valor = valor.substring(0, 11);
    
    // Aplica a máscara
    let formato = '';
    if (valor.length > 0) {
        formato = `(${valor.substring(0, 2)}`;
    }
    if (valor.length > 2) {
        formato += `) ${valor.substring(2, 7)}`;
    }
    if (valor.length > 7) {
        formato += `-${valor.substring(7, 11)}`;
    }
    
    campo.value = formato;
    
    if (posicaoCursor === 1 && valor.length > 2) {
        campo.setSelectionRange(4, 4); //posiciona apos ddd
    } else if (posicaoCursor === 4 && valor.length > 7) {
        campo.setSelectionRange(10, 10); //posiciona apos o 5 digito
    }
}
//vai formatar o CPF ao digitar
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
                formatado += num.substring(6);}
        } else {
            formatado += num.substring(3);}
    } else {
        formatado = num; }

    input.value = formatado;
}

  // Abrir o modal
  document.getElementById("openModal").addEventListener("click", function(event) {
    event.preventDefault(); // evita o comportamento padrão do link
    document.getElementById("editModal").style.display = "block";
  });

  // Fechar o modal
  document.getElementById("closeModal").addEventListener("click", function() {
    document.getElementById("editModal").style.display = "none";
  });

  // Fechar ao clicar fora do modal
  window.addEventListener("click", function(event) {
    var modal = document.getElementById("editModal");
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });





  // Abrir o modal
  document.getElementById("openLogoutModal").addEventListener("click", function(event) {
    event.preventDefault(); // evita o comportamento padrão do link
    document.getElementById("logoutModal").style.display = "block";
  });

  // Fechar o modal
  document.getElementById("closeLogoutModal").addEventListener("click", function() {
    document.getElementById("logoutModal").style.display = "none";
  });

  // Fechar ao clicar fora do modal
  window.addEventListener("click", function(event) {
    var modal = document.getElementById("logoutModal");
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });


  // Abrir o modal
  document.getElementById("openModalAddExame").addEventListener("click", function(event) {
    event.preventDefault(); // evita o comportamento padrão do link
    document.getElementById("AddExameModal").style.display = "block";
  });

  // Fechar o modal
  document.getElementById("closeModalAddExame").addEventListener("click", function() {
    document.getElementById("AddExameModal").style.display = "none";
  });

  // Fechar ao clicar fora do modal
  window.addEventListener("click", function(event) {
    var modal = document.getElementById("AddExameModal");
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });





  // Abrir o modal Alerta
  document.getElementById("openAlerta").addEventListener("click", function(event) {
    event.preventDefault(); // evita o comportamento padrão do link
    document.getElementById("alertaModal").style.display = "block";
  });

  // Fechar o modal Alerta
  document.getElementById("closeAlertaModal").addEventListener("click", function() {
    document.getElementById("alertaModal").style.display = "none";
  });

  // Fechar ao clicar fora do modal Alerta
  window.addEventListener("click", function(event) {
    var modal = document.getElementById("alertaModal");
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });

  document.addEventListener('DOMContentLoaded', function() {
        const fotoInput = document.getElementById('fotoInput');
        const previewImage = document.getElementById('previewImage');
        const imagePreviewLabel = document.getElementById('imagePreviewLabel');

        fotoInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImage.src = e.target.result;
                    imagePreviewLabel.style.display = 'block'; // Mostra o label
                };
                reader.readAsDataURL(file);
            } else {
                imagePreviewLabel.style.display = 'none'; // Esconde o label se nenhum arquivo for selecionado
                previewImage.src = ''; // Limpa a pré-visualização
            }
        });
    });
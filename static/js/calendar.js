// Variáveis globais para o calendário e formulário
    let currentSelectedDate = null; // A data selecionada no calendário principal (objeto Date)
    let currentFormStep = 0; // Índice do passo do formulário (0-3)

    // Dados de agendamento sendo construídos (ID do exame e médico)
    let newAgendamentoData = {
        data: null, // YYYY-MM-DD string
        exame_id: null,
        exame_nome: null,
        medico_id: null,
        medico_nome: null,
        horario: null // HH:MM string
    };

    const horarios_funcionamento_str = window.horariosFuncionamentoGlobal;
    const agendamentos_usuario_logado = window.agendamentosUsuarioLogadoGlobal;
    console.log("JS: Agendamentos recebidos do HTML:", agendamentos_usuario_logado); // DEBUG


    // --- FUNÇÕES DE CALENDÁRIO PRINCIPAL ---
    let currentMonthDisplay = new Date().getMonth();
    let currentYearDisplay = new Date().getFullYear();

    function createMainCalendar(year, month) {
        const calendarGrid = document.getElementById('calendarGrid');
        // Limpa as células de dias (mantém os dias da semana)
        while (calendarGrid.children.length > 7) {
            calendarGrid.removeChild(calendarGrid.lastChild);
        }

        const monthNames = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ];

        document.getElementById('calendarHeader').textContent = `${monthNames[month]} ${year}`;

        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startDayOfWeek = firstDay.getDay(); // 0 = Domingo, 6 = Sábado
        const totalDays = lastDay.getDate();

        // Adiciona células vazias para os dias antes do 1º do mês
        for (let i = 0; i < startDayOfWeek; i++) {
            const emptyCell = document.createElement('div');
            emptyCell.textContent = '';
            calendarGrid.appendChild(emptyCell);
        }

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        for (let day = 1; day <= totalDays; day++) {
            const dateCell = document.createElement('div');
            dateCell.textContent = day;

            const cellDate = new Date(year, month, day);
            cellDate.setHours(0, 0, 0, 0);

            // Formata a data para comparação com agendamentos existentes
            const formattedCellDate = cellDate.toISOString().split('T')[0];
            console.log(`DEBUG JS: Verificando dia ${formattedCellDate}`); // <--- ADICIONE ESTE CONSOLE.LOG
            // Verifica se há agendamentos para este dia (do usuário logado)
            const hasAppointments = agendamentos_usuario_logado.some(a => a.data === formattedCellDate);
            console.log(`DEBUG JS: Dia ${formattedCellDate} tem agendamento? ${hasAppointments}`); // <--- ADICIONE ESTE CONSOLE.LOG

            if (hasAppointments) {
                dateCell.classList.add('has-agendamento-dot'); // Adiciona um marcador visual
                console.log(`DEBUG JS: Adicionada classe 'has-agendamento-dot' ao dia ${formattedCellDate}`); // <--- ADICIONE ESTE CONSOLE.LOG
            }

            if (cellDate < today) {
                dateCell.style.color = '#ccc';
                dateCell.style.cursor = 'default';
                dateCell.classList.add('past-day'); // Nova classe para dias passados
            } else {
                dateCell.style.cursor = 'pointer';
                dateCell.addEventListener('click', () => {
                    currentSelectedDate = cellDate; // Armazena a data selecionada como objeto Date
                    newAgendamentoData.data = formattedCellDate; // Salva a data formatada (YYYY-MM-DD)
                    document.getElementById('agendamentoDataInput').value = formattedCellDate; // Preenche input hidden
                    document.getElementById('revData').textContent = currentSelectedDate.toLocaleDateString('pt-BR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }); // Preenche revisão

                    openDayAppointmentsModal(formattedCellDate); // Passa a data formatada para a função
                });
            }

            if (cellDate.getTime() === today.getTime()) {
                dateCell.classList.add('today');
            }

            calendarGrid.appendChild(dateCell);
        }
    }

    function prevMonth() {
        currentMonthDisplay--;
        if (currentMonthDisplay < 0) {
            currentMonthDisplay = 11;
            currentYearDisplay--;
        }
        createMainCalendar(currentYearDisplay, currentMonthDisplay);
    }

    function nextMonth() {
        currentMonthDisplay++;
        if (currentMonthDisplay > 11) {
            currentMonthDisplay = 0;
            currentYearDisplay++;
        }
        createMainCalendar(currentYearDisplay, currentMonthDisplay);
    }

    // --- MODAL 1: Listar Consultas do Dia ---
   const dayAppointmentsModal = document.getElementById('dayAppointmentsModal');
const closeDayAppointmentsModalBtn = document.getElementById('closeDayAppointmentsModal');
const selectedDateTitle = document.getElementById('selectedDateTitle');
const appointmentsList = document.getElementById('appointmentsList');
const openScheduleFormModalBtn = document.getElementById('openScheduleFormModalBtn');

async function openDayAppointmentsModal(formattedDate) {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    // A data displayDate é usada apenas para formatação do título do modal
    const displayDate = new Date(formattedDate + 'T00:00:00');
    selectedDateTitle.textContent = `Consultas em ${displayDate.toLocaleDateString('pt-BR', options)}`;
    appointmentsList.innerHTML = '<p>Carregando consultas...</p>'; // Mensagem de carregamento

    try {
        const response = await fetch(`/api/agendamentos_por_dia?selected_date=${formattedDate}`);
        const data = await response.json();

        if (data.success) {
            const appointmentsOnDay = data.agendamentos; // Lista de agendamentos para o dia
            if (appointmentsOnDay.length > 0) {
                appointmentsList.innerHTML = appointmentsOnDay.map(appt => `
                    <div class="appointment-item">
                        <strong>${appt.exame_nome}</strong> - ${appt.hora}<br>
                        <span>Com ${appt.medico_nome}</span>
                        <button class="cancel-appointment-btn" data-id="${appt.id}">Cancelar</button>
                    </div>
                `).join('');

                // Adicionar event listeners aos botões de cancelar APÓS eles serem inseridos no DOM
                document.querySelectorAll('.cancel-appointment-btn').forEach(button => {
                    button.addEventListener('click', async (event) => {
                        const appointmentIdToCancel = event.target.dataset.id;
                        if (confirm('Tem certeza que deseja cancelar este agendamento?')) {
                            await cancelAppointment(appointmentIdToCancel, formattedDate); // Passa a data formatada
                        }
                    });
                });

            } else {
                appointmentsList.innerHTML = '<p>Nenhuma consulta agendada para esta data.</p>';
            }
        } else {
            appointmentsList.innerHTML = `<p style="color: red;">Erro: ${data.message || 'Não foi possível carregar as consultas.'}</p>`;
            console.error('Erro ao carregar agendamentos:', data.message);
        }
    } catch (error) {
        appointmentsList.innerHTML = '<p style="color: red;">Erro ao conectar com o servidor para buscar consultas.</p>';
        console.error('Erro de fetch:', error);
    }

    dayAppointmentsModal.style.display = 'block'; // Exibe o modal
}

closeDayAppointmentsModalBtn.addEventListener('click', () => {
    dayAppointmentsModal.style.display = 'none';
});


// --- NOVA FUNÇÃO: Cancelar Agendamento ---
async function cancelAppointment(appointmentId, currentViewedDate) {
    try {
        const response = await fetch(`/api/agendamentos/${appointmentId}`, {
            method: 'DELETE', // Usar o método HTTP DELETE
            headers: {
                'Content-Type': 'application/json' // Opcional, mas boa prática para DELETE
            }
        });
        const data = await response.json(); // Tenta ler a resposta como JSON

        if (data.success) {
            alert(data.message);
            dayAppointmentsModal.style.display = 'none'; // Fecha o modal de consultas

            // IMPORTANTE: Atualizar o calendário principal para remover o ponto do dia, se for o último agendamento
            // e reabrir o modal para a data para refletir a mudança
            createMainCalendar(currentYearDisplay, currentMonthDisplay); // Recarrega o calendário principal para atualizar os pontos
            openDayAppointmentsModal(currentViewedDate); // Reabre o modal de consultas do dia para mostrar a lista atualizada

            // Opcional: Remover o agendamento da lista `agendamentos_usuario_logado` para que o ponto do calendário seja atualizado sem recarregar a página inteira
            // Isso é um pouco mais complexo porque `agendamentos_usuario_logado` está no escopo global e precisa ser atualizado corretamente
            // Find the index of the appointment to remove from the global list
            const indexToRemove = agendamentos_usuario_logado.findIndex(
                appt => appt.id === parseInt(appointmentId) // Assegure-se de que o tipo de 'id' é o mesmo (int)
            );
            if (indexToRemove > -1) {
                agendamentos_usuario_logado.splice(indexToRemove, 1);
            }


        } else {
            alert('Erro ao cancelar agendamento: ' + (data.message || 'Tente novamente.'));
            console.error('Erro no cancelamento:', data.message);
        }
    } catch (error) {
        alert('Erro ao conectar com o servidor para cancelar agendamento. Verifique o console.');
        console.error('Erro de fetch no cancelamento:', error);
    }
}

    // --- MODAL 2: Formulário de Agendamento Multi-passo ---
    const scheduleFormModal = document.getElementById('scheduleFormModal');
    const closeScheduleFormModalBtn = document.getElementById('closeScheduleFormModal');
    const scheduleModalTitle = document.getElementById('scheduleModalTitle');
    const formSteps = document.querySelectorAll('#scheduleFormModal .step');
    const prevFormBtn = document.getElementById('prevBtn');
    const nextFormBtn = document.getElementById('nextBtn'); // Este botão será desativado, o avanço é por clique na opção
    const confirmAgendamentoBtn = document.getElementById('confirmAgendamentoBtn');

    // Inputs ocultos para enviar os dados do formulário
    const agendamentoDataInput = document.getElementById('agendamentoDataInput');
    const agendamentoExameInput = document.getElementById('agendamentoExameInput');
    const agendamentoMedicoInput = document.getElementById('agendamentoMedicoInput');
    const agendamentoHorarioInput = document.getElementById('agendamentoHorarioInput');

    // Abre o Modal 2 quando o botão "Agendar Nova Consulta" é clicado no Modal 1
    openScheduleFormModalBtn.addEventListener('click', () => {
        dayAppointmentsModal.style.display = 'none'; // Fecha o Modal 1
        scheduleFormModal.style.display = 'block'; // Abre o Modal 2
        currentFormStep = 0; // Reseta para o primeiro passo
        showFormStep(currentFormStep);

        // A data já deve estar em newAgendamentoData.data e agendamentoDataInput.value
        // se o usuário clicou em uma célula do calendário antes.
    });

    closeScheduleFormModalBtn.addEventListener('click', () => {
        scheduleFormModal.style.display = 'none';
        // Reseta os dados de agendamento e inputs ocultos ao fechar o modal
        newAgendamentoData = { data: null, exame_id: null, exame_nome: null, medico_id: null, medico_nome: null, horario: null };
        agendamentoDataInput.value = '';
        agendamentoExameInput.value = '';
        agendamentoMedicoInput.value = '';
        agendamentoHorarioInput.value = '';
        // Limpar seleção visual dos botões
        document.querySelectorAll('.step-option-btn.selected').forEach(btn => btn.classList.remove('selected'));
    });

    function showFormStep(stepIndex) {
        formSteps.forEach((step, index) => {
            step.style.display = (index === stepIndex) ? 'block' : 'none';
        });

        // Atualiza o título do modal e visibilidade dos botões de navegação do formulário
        switch (stepIndex) {
            case 0: // Passo 1: Escolher Exame
                scheduleModalTitle.textContent = 'Passo 1: Escolha o exame';
                prevFormBtn.style.display = 'none';
                nextFormBtn.style.display = 'none'; // Não tem botão próximo, avança por seleção
                confirmAgendamentoBtn.style.display = 'none';
                break;
            case 1: // Passo 2: Escolher Médico
                scheduleModalTitle.textContent = 'Passo 2: Escolha o médico';
                prevFormBtn.style.display = 'inline-block';
                nextFormBtn.style.display = 'none'; // Não tem botão próximo, avança por seleção
                confirmAgendamentoBtn.style.display = 'none';
                break;
            case 2: // Passo 3: Escolher Horário
                scheduleModalTitle.textContent = 'Passo 3: Escolha o horário';
                populateHorarioOptions(); // Popula horários ao entrar neste passo
                prevFormBtn.style.display = 'inline-block';
                nextFormBtn.style.display = 'none'; // Não tem botão próximo, avança por seleção
                confirmAgendamentoBtn.style.display = 'none';
                break;
            case 3: // Passo 4: Revisar Dados
                scheduleModalTitle.textContent = 'Passo 4: Revisar Agendamento';
                displayReviewDetails();
                prevFormBtn.style.display = 'inline-block';
                nextFormBtn.style.display = 'none';
                confirmAgendamentoBtn.style.display = 'inline-block'; // Botão final visível
                break;
        }
        // Garante que o botão nextFormBtn esteja sempre invisível, já que o avanço é por clique nas opções.
        // nextFormBtn.style.display = 'none';
    }

    function prevFormStep() {
        if (currentFormStep > 0) {
            currentFormStep--;
            showFormStep(currentFormStep);
        }
    }

    // Funções de seleção de passos (chamadas pelos botões dentro dos steps)
    function selectExame(buttonElement) {
        newAgendamentoData.exame_id = buttonElement.dataset.id;
        newAgendamentoData.exame_nome = buttonElement.dataset.nome;
        agendamentoExameInput.value = buttonElement.dataset.id;
        // Adiciona/remove classe 'selected' para feedback visual
        document.querySelectorAll('#exameOptionsContainer .step-option-btn').forEach(btn => btn.classList.remove('selected'));
        buttonElement.classList.add('selected');
        // Avança para o próximo passo
        currentFormStep = 1; // Vai para o Passo 2: Escolher Médico
        showFormStep(currentFormStep);
    }

    function selectMedico(buttonElement) {
        newAgendamentoData.medico_id = buttonElement.dataset.id;
        newAgendamentoData.medico_nome = buttonElement.dataset.nome;
        agendamentoMedicoInput.value = buttonElement.dataset.id;
        document.querySelectorAll('#medicoOptionsContainer .step-option-btn').forEach(btn => btn.classList.remove('selected'));
        buttonElement.classList.add('selected');
        // Avança para o próximo passo
        currentFormStep = 2; // Vai para o Passo 3: Escolher Horário
        showFormStep(currentFormStep);
    }

    async function populateHorarioOptions() {
        const container = document.getElementById('horarioOptionsContainer');
        container.innerHTML = '<p>Carregando horários...</p>'; // Mensagem de carregamento

        if (!newAgendamentoData.medico_id || !newAgendamentoData.data) {
            container.innerHTML = '<p style="color: red;">Selecione um médico e uma data para ver os horários.</p>';
            return;
        }

        try {
            const response = await fetch(`/api/horarios_ocupados?medico_id=${newAgendamentoData.medico_id}&selected_date=${newAgendamentoData.data}`);
            const data = await response.json();

            if (data.success) {
                const ocupados = data.ocupados; // Lista de horários HH:MM já ocupados
                container.innerHTML = ''; // Limpa o container

                let hasAvailable = false;
                horarios_funcionamento_str.forEach(horario_total => {
                    const isOccupied = ocupados.includes(horario_total);
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.textContent = horario_total;
                    btn.classList.add('step-option-btn');
                    if (isOccupied) {
                        btn.classList.add('occupied');
                        btn.disabled = true; // Desabilita botões de horários ocupados
                        btn.title = 'Horário ocupado';
                    } else {
                        btn.classList.add('available');
                        hasAvailable = true;
                        if (newAgendamentoData.horario === horario_total) { // Mantém seleção visual
                            btn.classList.add('selected');
                        }
                        btn.onclick = () => {
                            newAgendamentoData.horario = horario_total;
                            agendamentoHorarioInput.value = horario_total;
                            document.querySelectorAll('#horarioOptionsContainer .step-option-btn').forEach(b => b.classList.remove('selected'));
                            btn.classList.add('selected');
                            // Não avança automaticamente aqui, o usuário clica em "Confirmar"
                            // currentFormStep = 3; showFormStep(currentFormStep); // Moveria para a revisão imediatamente
                        };
                    }
                    container.appendChild(btn);
                });

                if (!hasAvailable) {
                    container.innerHTML = '<p>Nenhum horário disponível para este médico e data.</p>';
                }
            } else {
                container.innerHTML = `<p style="color: red;">Erro: ${data.message || 'Não foi possível carregar horários.'}</p>`;
                console.error('Erro ao carregar horários:', data.message);
            }
        } catch (error) {
            container.innerHTML = '<p style="color: red;">Erro ao conectar com servidor para horários.</p>';
            console.error('Erro de fetch:', error);
        }
    }

    function displayReviewDetails() {
        document.getElementById('revData').textContent = newAgendamentoData.data || 'Não selecionada';
        document.getElementById('revExame').textContent = newAgendamentoData.exame_nome || 'Não selecionado';
        document.getElementById('revMedico').textContent = newAgendamentoData.medico_nome || 'Não selecionado';
        document.getElementById('revHorario').textContent = newAgendamentoData.horario || 'Não selecionado';
    }

    // Submissão do formulário final via Fetch API
    document.getElementById('agendamentoForm').addEventListener('submit', async (event) => {
        event.preventDefault(); // Impede o envio padrão do formulário

        // Validação final antes de enviar (já existe no seu código, mantida)
        if (!newAgendamentoData.data || !newAgendamentoData.exame_id || !newAgendamentoData.medico_id || !newAgendamentoData.horario) {
        
            return;
        }

        // Preenche os inputs hidden do formulário antes de submeter (já existe no seu código, mantida)
        agendamentoDataInput.value = newAgendamentoData.data;
        agendamentoExameInput.value = newAgendamentoData.exame_id;
        agendamentoMedicoInput.value = newAgendamentoData.medico_id;
        agendamentoHorarioInput.value = newAgendamentoData.horario;

        try {
            const formData = new FormData(event.target);
            const response = await fetch('/agendar', {
                method: 'POST',
                body: formData // Envia o FormData diretamente
            });

            // PRIMEIRA VERIFICAÇÃO: A resposta HTTP foi bem-sucedida (status 2xx)?
            // Se não, pode ser um erro 4xx ou 5xx que ainda é um JSON, mas não é "success"
            // ou pode ser um erro que nem JSON retorna.
            if (!response.ok) {
                // Tenta ler o erro do servidor, se a resposta for JSON
                const errorData = await response.json().catch(() => null); // Tenta ler JSON, se falhar, retorna null
                let errorMessage = errorData && errorData.message ? errorData.message : 'Erro desconhecido ao agendar. Status: ' + response.status;
                
            
                console.error('Erro de servidor:', response.status, errorMessage);
                // Não recarrega a página em caso de erro, para o usuário ver a mensagem.
                window.location.reload(); // Recarrega para ver o novo agendamento
                return; // Sai da função após o
            }

            // SE CHEGOU AQUI, a resposta HTTP foi 2xx, então tenta ler o JSON
            const data = await response.json();

            if (data.success) { // SE O JSON INDICA SUCESSO
            
                scheduleFormModal.style.display = 'none';
                window.location.reload(); // Recarrega para ver o novo agendamento
            } else { // SE O JSON INDICA FALHA LÓGICA (data.success é false)
                
                console.error('Falha lógica no agendamento:', data.message);
                // Não recarrega a página, para o usuário poder corrigir ou tentar novamente
                window.location.reload(); // Recarrega para ver o novo agendamento
            }
        } catch (error) { // ESTE CATCH SÓ DEVE PEGAR ERROS DE REDE OU DE PARSEAMENTO DE JSON
            
            console.error('Erro de fetch no agendamento:', error);
            window.location.reload(); // Recarrega para ver o novo agendamento
            // Não recarrega a página
        }
    });


    // --- INICIALIZAÇÃO ---
    document.addEventListener('DOMContentLoaded', () => {
        createMainCalendar(currentYearDisplay, currentMonthDisplay);

        // Event listeners para fechar modais ao clicar fora
        window.addEventListener('click', (event) => {
            if (event.target === dayAppointmentsModal) {
                dayAppointmentsModal.style.display = 'none';
            }
            if (event.target === scheduleFormModal) {
                scheduleFormModal.style.display = 'none';
            }
            // Mantenha aqui a lógica para fechar outros modais (logoutModal, deleteModal, etc.)
        });
    });
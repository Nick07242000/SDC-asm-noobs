.text
    .global gini_convert          # visible para C

gini_convert:
    # ========================= Frame ===================================
    pushq   %rbp                  # guarda el frame pointer del caller
    movq    %rsp, %rbp            # establece el nuevo frame pointer

    # ========================= Convert =================================
    # lee el float de 32 bits en xmm0
    # convierte el float a int truncando hacia cero
    # escribe el entero de 64 bits en rax
    cvttss2siq %xmm0, %rax        # rax = (int) xmm0

    # ========================= Add =====================================
    addq    $1, %rax              # rax = rax + 1

    # ========================= Return ==================================
    popq    %rbp                  # restaura el frame pointer del caller
    ret                           # el resultado queda disponible en rax
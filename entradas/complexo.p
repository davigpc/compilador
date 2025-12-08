// Função recursiva para calcular fatorial
fn fatorial(n: int) -> int {
    if n <= 1 {
        return 1;
    } else {
        return n * fatorial(n - 1);
    }
    return 1;
}

// Função para testar tipos float
fn area_circulo(raio: float) -> float {
    let pi: float;
    pi = 3.14159;
    return pi * raio * raio;
}

fn main() {
    // Declaração de múltiplos tipos
    let i, max: int;
    let resultado: int;
    let raio, area: float;
    let status: char;

    max = 5;
    i = 0;
    status = 'A';

    // Teste de while com chamada de função
    while i < max {
        resultado = fatorial(i);
        println("Fatorial de {} eh {}", i, resultado);
        i = i + 1;
    }

    // Teste de float e if/else aninhado
    raio = 2.5;
    area = area_circulo(raio);

    if area > 10.0 {
        if status == 'A' {
            println("Area grande e status Ativo: {}", area);
        } else {
            println("Area grande mas status Inativo");
        }
    } else {
        println("Area pequena: {}", area);
    }

    // Expressão complexa para testar precedência na AST
    // A AST deve agrupar (2 * 10) e (5 / 1) antes das somas/subtrações
    resultado = 100 - 2 * 10 + 5 / 1;
}
#include <iostream>
#include <fstream>
#include <muParser.h>
#include <string>
#include <tuple>
#include <cmath>
#include <limits>

double x;

using namespace std;

void lerTxt(tuple<mu::Parser, double, double, double, int, mu::Parser>& dados) {
    ifstream arquivo("entrada.txt");
    string linha;

    if (!arquivo.is_open()) {
        cout << "Erro ao abrir o arquivo!" << endl;
        return;
    }

    getline(arquivo, linha);
    auto& func = get<0>(dados);
    func.DefineVar("x", &x);
    func.SetExpr(linha);

    getline(arquivo, linha);
    get<1>(dados) = stod(linha);

    getline(arquivo, linha);
    get<2>(dados) = stod(linha);

    getline(arquivo, linha);
    get<3>(dados) = stod(linha);

    getline(arquivo, linha);
    get<4>(dados) = stoi(linha);

    getline(arquivo, linha);
    auto& func2 = get<5>(dados);
    func2.DefineVar("x", &x);
    func2.SetExpr(linha);
}

bool existeIntervalo(mu::Parser &func, double a, double b) {
    func.DefineVar("x", &x);

    x = a;
    double fa = func.Eval();

    x = b;
    double fb = func.Eval();

    return (fa * fb < 0) || (fa == 0) || (fb == 0);
}

double derivada(mu::Parser& f, double x0) {
    double h = 1e-6;

    x = x0 + h;
    double f1 = f.Eval();

    x = x0 - h;
    double f2 = f.Eval();

    return (f1 - f2) / (2*h);
}

double bissecao(tuple<mu::Parser, double, double, double, int, mu::Parser> dados) {
    auto& func = get<0>(dados);
    double a = get<1>(dados);
    double b = get<2>(dados);
    double prec = get<3>(dados);
    int itMax = get<4>(dados);
    int it = 1;
    double x0 = 0.0;
    double root = numeric_limits<double>::quiet_NaN();
    
    func.DefineVar("x", &x);
    
    if(!existeIntervalo(func, a, b)){
        return root;
    }
    
    while (fabs(b - a) > prec && it <= itMax) {
        x0 = (a + b) / 2.0;

        x = a;
        double fa = func.Eval();
        x = b;
        double fb = func.Eval();
        x = x0;
        double fx0 = func.Eval();

        if (fa * fx0 > 0) {
            a = x0;
        } else {
            b = x0;
        }

        it++;
    }

    x0 = (a + b) / 2.0;
    root = x0;
    return root;
}

double MIL(tuple<mu::Parser, double, double, double, int, mu::Parser> dados){
    auto& f = get<0>(dados);
    double a = get<1>(dados);
    double b = get<2>(dados);
    double prec = get<3>(dados);
    int itMax = get<4>(dados);
    auto& g = get<5>(dados);
    int it = 1;
    double x0 = (a + b) / 2;
    double x1 = numeric_limits<double>::quiet_NaN();
    double root = numeric_limits<double>::quiet_NaN();

    f.DefineVar("x", &x);
    g.DefineVar("x", &x);

    x = x0;
    double fx0 = f.Eval();

    if(fabs(fx0) < prec){
        root = x0;
        return root;
    }

    while(true){
        x1 = g.Eval();
        x = x1;
        double fx1 = f.Eval();

        if(fabs(fx1) < prec || it >= itMax || fabs(x1 - x0) < prec){
            root = x1;
            break;
        }
        
        x0 = x1;
        it++;
    }

    return root;
}

double Newton(tuple<mu::Parser, double, double, double, int, mu::Parser> dados){
    auto& f = get<0>(dados);
    double a = get<1>(dados);
    double b = get<2>(dados);
    double prec = get<3>(dados);
    int itMax = get<4>(dados);
    int it = 1;
    double x0 = (a + b) / 2;
    double x1 = numeric_limits<double>::quiet_NaN();
    double root = numeric_limits<double>::quiet_NaN();

    f.DefineVar("x", &x);

    x = x0;
    double fx = f.Eval();
    
    if(fabs(fx) > prec){
        double fxLinha = derivada(f, x0);
        x1 = x0 - (fx / fxLinha);
        x = x1;
        fx = f.Eval();
        while(fabs(fx) > prec && it <= itMax && fabs(x1 - x0) > prec){
            it++;
            x0 = x1;
            fxLinha = derivada(f, x0);
            x1 = x0 - (fx / fxLinha);
            x = x1;
            fx = f.Eval();
        }
        root = x1;
    }else{
        root = x0;
    } 
    return root; 
}

double Secante(tuple<mu::Parser, double, double, double, int, mu::Parser> dados){
    auto& f = get<0>(dados);
    double x0 = get<1>(dados);
    double x1 = get<2>(dados);
    double prec = get<3>(dados);
    int itMax = get<4>(dados);
    int it = 1;
    double x2 = numeric_limits<double>::quiet_NaN();
    double fx2 = numeric_limits<double>::quiet_NaN();
    double root = numeric_limits<double>::quiet_NaN();

    f.DefineVar("x", &x);

    x = x0;
    double fx0 = f.Eval();
    
    x = x1;
    double fx1 = f.Eval();

    if(fabs(fx0) < prec){
        root = x0;
    }else if(fabs(fx1) < prec){
        root = x1;
    }else{
        while(true){
            x2 = x1 - ((fx1 * (x1 - x0)) / (fx1 -fx0));
            x = x2;
            fx2 = f.Eval();

            if(fabs(fx2) < prec || fabs(x2 - x1) < prec || it >= itMax)
                break;
            
            x0 = x1;
            fx0 = fx1;
            x1 = x2;
            fx1 = fx2;

            it++;
        }
        root = x2;
    }
    return root;
}

double regulaFalsi(tuple<mu::Parser, double, double, double, int, mu::Parser> dados){
    auto& f = get<0>(dados);
    double a = get<1>(dados);
    double b = get<2>(dados);
    double prec = get<3>(dados);
    int itMax = get<4>(dados);
    int it = 1;
    double x0 = numeric_limits<double>::quiet_NaN();
    double fx = numeric_limits<double>::quiet_NaN();
    double root = numeric_limits<double>::quiet_NaN();

    f.DefineVar("x", &x);

    if(!existeIntervalo(f, a, b)){
        return root;
    }

    x = a;
    double fa = f.Eval();
    x = b;
    double fb = f.Eval();

    if(fabs(b - a) < prec){
        root = a;
    }else if(fabs(fa) < prec || fabs(fb) < prec){
        root = a;
    }else{
        while(true){
            x = a;
            double faLoop = f.Eval();
            x = b;
            double fbLoop = f.Eval();

            x0 = (a * fbLoop - b * faLoop) / (fbLoop - faLoop);
            x = x0;
            fx = f.Eval();

            if(fabs(fx) < prec || it >= itMax){
                root = x0;
                break;
            }else if(faLoop * fx > 0){
                a = x0;
                fa = fx;
            }else{
                b = x0;
                fb = fx;
            }

            if(fabs(b - a) < prec){
                root = a;
                break;
            }

            it++;
        }
    }
    return root;
}

int main() {
    tuple<mu::Parser, double, double, double, int, mu::Parser> dados;
    lerTxt(dados);
    double raizBissecao = bissecao(dados);
    double raizMil = MIL(dados);
    double raizNewton = Newton(dados);
    double raizSecante = Secante(dados);
    double raizRegulaFalsi = regulaFalsi(dados);

    ofstream arquivo("saida.txt");
    if (!arquivo.is_open()) {
        cout << "Erro ao abrir o arquivo!" << endl;
        return 1;
    }
    arquivo << raizBissecao << endl;
    arquivo << raizMil << endl;
    arquivo << raizNewton << endl;
    arquivo << raizSecante << endl;
    arquivo << raizRegulaFalsi << endl;

    return 0;
}

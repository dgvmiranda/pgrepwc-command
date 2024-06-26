### Grupo: SO-TI-12
### Aluno 1: Renato Pereira (fc52599)
### Aluno 2: Duarte Fernandes (fc55327)
### Aluno 3: Duarte Miranda (fc58631)

### Exemplos de comandos para executar o pgrepwc:

1) ./pgrepwc -c -l if -p 2 pgrepwc_processos.py
2) ./pgrepwc -c -l processes -p pgrepwc_processos.py 
3) ./pgrepwc -c -l processes -p file4.txt
4) ./pgrepwc -c -l processes file3.txt
5) ./pgrepwc 
6) ./pgrepwc ola file1.txt file2.txt file3.txt file4.txt -p 4 -c -l
7) ./pgrepwc ola file2.txt -e 500 -c -l -p 50
8) ./pgrepwc -c -l -p 10 -e 1000 ola file2.txt file3.txt
9) ./pgrepwc -c -l -p 5 -e 20 ola file4.txt
10) ./pgrepwc ola ../file1.txt -c -l -p 5 -e 100


### Limitações da implementação:
- nos processos a opção -e no ficheiro file1.txt quando o numero ce processo é muito alto (testado com 100 processos) a execução do
comando é extremamente lenta e maioritariamente a linha de comandos fecha. Quando só temos a linha de comandos a executar o comando
consegue processar com um numero de processos mais elevado. Por isso achomos que o problema se deve ao softwere das maquinas
virtuais da universidade que não têm capacidade para executar um numero de processos muito elevado.

- Na opção -e o ficheiro 1 é extremamente demorado e a opcção CTRL+C não conseguimos que trabalhasse como suposto, este termina o pai e sai.

- Não fomos capazes dentro do tempo atribuido de conseguir que a opção -e funcionasse para mais que um fichiero.

### Abordagem para a divisão dos ficheiros:

- na opção sem -e os ficheiros em 1 lugar são ordenados e depois distribuidos por listas da forma mais igual possivel. Se o tamanho total dos ficheiros numa lista for menor
do que na segunda ele vai adicionar o valor do ficheiro a essa lista.     
Se o numero de ficheiros for igual ao numero de processos o processo pai vai adicionar um ficheiro a cada lista

- na opção -e o processo pai lê todas as linhas do ficheiro e vai criar listas que representam os blocos de trabalho em que a cada iteração vai ver se uma linha cabe no bloco



### Outras informações pertinentes:

-Nos exemplos de comando são propositadamente dados comandos que não funcionam para demonstrar

- Estamos a assumir que o processo pai não partecipa na procura quando o numero de processo é maior do que 0 (-p n > 0)

- o nosso comando consegue aceitar qualquer ficheiro desde que tenha uma extensão (tem de ter '.' no nome) visto que é 
assim que o nosso programa faz a distinção entre os ficheiros e a palvra a procurar

- o nosso comando não procura pela palavra isoladamente ele procura pela ordem de caracteres fornecida e não é case sensitive

- Na impressão de dados parciais, em que o pai é suposto escrever para o stdout de 3 em 3 segundos, não conseguimos que este fosse preciso, acaba por fazer a impressão de
resultados aproximadamente de 3 em 3 segundos.

- No tratamento do sinal CTRL+C tivemos dificuldade na interpretação por isso questionamos no forum, e tentamos resolver tendo em conta a resposta do Professor Alysson:
      "O mais correto é terminar logo e imprimir os resultados parciais.
       Note que no enunciado é dito "Por seu turno, o processo pai escreve para stdout o número de ocorrências encontradas de cada a palavra a pesquisar ou
       o número de linhas onde cada palavra foi encontrada até ao momento, considerando apenas os ficheiros que foram processados pelos processos."
       Isso significa que, para quem está cuidar dos prints das linhas para que não apareçam intercalados, não é preciso imprimi-las, apenas os contadores e, 
       opcionalmente, outras infos sobre o estado da computação são suficientes (ex. terminou ficheiro A e B, e processou até a linha X do ficheiro C)."

 Com isto quando o nosso programa corre durante a pesquisa vão sendo impressos resultados parciais no fim da pesquisa são impressas as linhas onde foram encontradas a palvra
 e também os resultados finais. Se o processamento for interrrompido a meio apenas são apresentados os resultados obtidos até esse ponto.

- Não tivemos tempo para poder comentar uma boa parte do trabalho. Ao contrário de como na 1a fase.


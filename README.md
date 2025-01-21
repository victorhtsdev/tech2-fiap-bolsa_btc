# Pipeline de Dados Big Data Serverless Bovespa

## Descrição

Este projeto foi desenvolvido como parte do curso de pós-graduação em **Machine Learning Engineering** da **FIAP**, durante um desafio técnico relacionado a **MLOps**. O objetivo foi projetar e implementar um pipeline de dados eficiente e automatizado.

---

## Tecnologias Utilizadas

- **Terraform**: Ferramenta de infraestrutura como código (IaC) para provisionamento e gestão dos recursos necessários.
- **GitHub Actions**: Automatização do pipeline por meio de workflows.
- **Cloud Provider**: AWS
- **Python**: Linguagem utilizada para scripts e automação.
- **Amazon S3**: Armazenamento de dados.
- **AWS Glue**: Serviço para ETL e catálogo de dados.
- **Apache Spark**: Framework para processamento distribuído de dados.
- **AWS Lambda**: Funções serverless para execução de código.
- **AWS Athena Notebook**: Consulta de dados diretamente no S3 usando SQL.

---

## Estrutura do Repositório

- `.github/workflows/`: Contém os arquivos de configuração do GitHub Actions.
- `infra/`: Contém os arquivos do Terraform para provisionamento da infraestrutura.
- `bolsa_script.py`: Script para rodar localmente e enviar o arquivo raw e parquet a ser processado pelo job do Glue.
- `lambda.py`: Código da função Lambda na AWS que serve para acionar o job do Glue.
- `reproc_bolsa_script.py`: Script utilizado para reprocessar algum arquivo, desenvolvido como suporte durante o desenvolvimento.
- `athena_notebook.ipynb`: Notebook utilizado para demonstrar o resultado do trabalho.

---

## Diagrama do Pipeline


 ![Diagrama do Pipeline](/documents/tech_challenge_2_diagrama.png)
---

## Resultados Obtidos

O objetivo principal deste trabalho foi desenvolver o pipeline de dados, e não realizar uma análise aprofundada dos dados. No entanto, o notebook athena_notebook.ipynb foi utilizado para demonstrar os resultados obtidos a partir dos dados capturados.

Os dados processados pelo pipeline foram armazenados no Amazon S3 e consultados utilizando o AWS Athena, permitindo a execução de consultas SQL diretamente sobre os dados no S3 de forma serverless. O notebook demonstrou como as consultas no Athena foram usadas para explorar e extrair informações relevantes.

O gráfico gerado no notebook ilustra as variações na quantidade teórica total das ações da Bovespa de um dia para o outro, destacando mudanças significativas, como inclusões, exclusões e rebalanceamentos de papéis, capturados no pipeline, como:

- O **lançamento de papéis** da Lojas Renner (LREN3) no dia 13 de dezembro.
- O **rebalanceamento da carteira teórica** da Bovespa no inicio de janeiro.

 ![Diagrama do Pipeline](/documents/notebook_plot.png)

---

## Autor

### Victor HTS.
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Perfil-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/victor-hugo-teles-de-santana-359ba260/)

---

## Licença

Este projeto é open-source sob a licença [MIT](LICENSE).


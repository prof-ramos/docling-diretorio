# DOCLING-DIRETORIO

Utilizando o docling que já está instalado globalmente, converta todos os arquivos de determinado diretório e os recursivos.
O código perguntará o caminho do diretório (via input). Após isso, o código processará todos os documentos ali dentro (mostrando a porcentagem com TQDM e colorama). Além disso, em caso de erro de algum documento o código pulará para o próximo e emitirá, também, no diretório de output um relatório com os arquivos que não foram devidamente processados.

# 📂 DOCLING-DIRETORIO

Este projeto permite converter todos os arquivos de um diretório (e seus subdiretórios) utilizando o **Docling** (já instalado globalmente).  
Ele foi pensado para automatizar a conversão em lote de documentos, exibindo progresso e gerando relatórios de erros.

---

## 🚀 Como funciona

1. Ao executar o código, será solicitado o **caminho do diretório** (via `input`).
2. Todos os arquivos presentes nesse diretório e nos seus subdiretórios serão processados.
3. Durante o processamento:
   - O progresso será exibido utilizando **TQDM** (barra de progresso).
   - As mensagens terão cores fornecidas pelo **Colorama**.
4. Em caso de erro em algum documento:
   - O programa **ignora o arquivo com falha** e continua o processamento dos demais.
   - É gerado um **relatório de erros** no diretório de saída, listando os arquivos que não foram processados corretamente.

---

## 📦 Dependências

Certifique-se de ter instalado previamente:

- [Docling](https://pypi.org/project/docling/) (instalado globalmente)
- [tqdm](https://pypi.org/project/tqdm/)
- [colorama](https://pypi.org/project/colorama/)

---

## ▶️ Execução

Para rodar o script:

```bash
python main.py
```

O programa pedirá o caminho do diretório que você deseja processar.

---

## 📑 Relatórios de erros

- Caso algum arquivo não seja processado, ele será listado em um **relatório gerado no diretório de output**.  
- Isso permite identificar rapidamente quais arquivos precisam ser revisados manualmente.

---

## 🛠️ Contribuindo

Sinta-se à vontade para abrir *issues* ou enviar *pull requests* com melhorias e correções.

---

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).
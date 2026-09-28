package com.geovani.alexiaultra;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.PopupMenu;
import android.widget.ScrollView;
import android.widget.TextView;
import android.provider.OpenableColumns;
import android.database.Cursor;
import android.os.Build;
import android.provider.Settings;
import android.content.ActivityNotFoundException;

import androidx.core.content.FileProvider;

import java.io.File;
import java.io.FileOutputStream;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

public class MainActivity extends Activity {

    private LinearLayout tela;
    private LinearLayout mensagens;
    private EditText campoMensagem;
    private EditText campoCodigo;
    
    // ============================================================
    // ARQUIVO SELECIONADO
    // ============================================================

    private String nomeArquivoSelecionado = "";
    private String conteudoArquivoSelecionado = "";

    private static final int REQUEST_SELECIONAR_ARQUIVO = 1001;

    private final ExecutorService executor =
            Executors.newSingleThreadExecutor();

    private final List<JSONObject> historico =
            new ArrayList<>();

    private static final String API_URL =
            "https://ultra-ia-pro.onrender.com/api/chat";

    private static final String PONTE_API_URL =
            "https://ultra-ia-pro.onrender.com/api/ponte/processar";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        entrarEmTelaCheia();
        criarInterface();
    }

    private void entrarEmTelaCheia() {

        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                        | View.SYSTEM_UI_FLAG_FULLSCREEN
                        | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                        | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
        );
    }

    private void criarInterface() {

        tela = new LinearLayout(this);
        tela.setOrientation(LinearLayout.VERTICAL);
        tela.setBackgroundColor(Color.rgb(8, 12, 20));

        // ============================================================
        // CABEÇALHO
        // ============================================================

        TextView titulo = new TextView(this);

        titulo.setText("🤖 Alex IA Ultra");
        titulo.setTextColor(Color.WHITE);
        titulo.setTextSize(22);
        titulo.setGravity(Gravity.CENTER);
        titulo.setPadding(20, 30, 20, 30);

        tela.addView(
                titulo,
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                )
        );

        // ============================================================
        // ➕ BOTÃO DE FERRAMENTAS
        // ============================================================

        Button botaoMais = new Button(this);

        botaoMais.setText("＋");
        botaoMais.setTextSize(22);
        botaoMais.setTextColor(Color.WHITE);

        botaoMais.setOnClickListener(v -> {

            PopupMenu menu =
                    new PopupMenu(
                            MainActivity.this,
                            botaoMais
                    );

            menu.getMenu().add("🖼️ Imagem");
            menu.getMenu().add("🎬 Vídeo");
            menu.getMenu().add("🔊 Voz");
            menu.getMenu().add("💻 Código");
            menu.getMenu().add("📎 Arquivo");
            menu.getMenu().add("🎭 Personagem");
            menu.getMenu().add("🧠 Memória");
            menu.getMenu().add("🗑️ Limpar chat");

            menu.setOnMenuItemClickListener(item -> {

                String ferramenta =
                        item.getTitle().toString();

                // ===================================================
                // 💻 CÓDIGO
                // ====================================================

                if (ferramenta.equals("💻 Código")) {

                   campoCodigo.requestFocus();

                   adicionarMensagem(
                           "💻 Modo Código ativado.\n\n"
                                   + "Cole o código na área da Ponte Alex v2 "
                                   + "e escreva abaixo o que você quer que "
                                   + "a Ponte faça."
                   );

                   return true;
                }

                // ====================================================
                // 📎 ARQUIVO
                // ====================================================

                if (ferramenta.equals("📎 Arquivo")) {

                    abrirSeletorDeArquivo();

                    return true;
                }

                // ====================================================
                // 🗑️ LIMPAR CHAT
                // ====================================================

                if (ferramenta.equals("🗑️ Limpar chat")) {

                    mensagens.removeAllViews();

                    adicionarMensagem(
                            "🗑️ Chat limpo."
                    );

                    return true;
                }

                // ====================================================
                // OUTRAS FERRAMENTAS
                // ====================================================

                adicionarMensagem(
                        "🧰 Ferramenta selecionada: "
                                + ferramenta
                );

                return true;
            });

            menu.show();
        });

        tela.addView(
                botaoMais,
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.WRAP_CONTENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                )
        );

        // ============================================================
        // ÁREA DE MENSAGENS
        // ============================================================

        ScrollView scroll = new ScrollView(this);

        mensagens = new LinearLayout(this);
        mensagens.setOrientation(LinearLayout.VERTICAL);
        mensagens.setPadding(20, 20, 20, 20);

        TextView boasVindas = new TextView(this);

        boasVindas.setText(
                "Olá! Eu sou a Alex IA Ultra.\n\n"
                        + "Agora estou conectada ao meu cérebro de IA."
        );

        boasVindas.setTextColor(Color.WHITE);
        boasVindas.setTextSize(17);
        boasVindas.setPadding(25, 25, 25, 25);

        mensagens.addView(boasVindas);

        scroll.addView(mensagens);

        tela.addView(
              scroll,
              new LinearLayout.LayoutParams(
                  ViewGroup.LayoutParams.MATCH_PARENT,
                  (int) (280 * getResources().getDisplayMetrics().density)
              )
        );
        // ============================================================
        // ÁREA DE DIGITAÇÃO
        // ============================================================

        LinearLayout entrada = new LinearLayout(this);
        entrada.setOrientation(LinearLayout.HORIZONTAL);
        entrada.setPadding(15, 15, 15, 15);

        campoMensagem = new EditText(this);

        campoMensagem.setHint("Digite uma mensagem...");
        campoMensagem.setHintTextColor(Color.LTGRAY);
        campoMensagem.setTextColor(Color.WHITE);
        campoMensagem.setTextSize(16);

        entrada.addView(
                campoMensagem,
                new LinearLayout.LayoutParams(
                        0,
                        ViewGroup.LayoutParams.WRAP_CONTENT,
                        1
                )
        );

        Button enviar = new Button(this);

        enviar.setText("Enviar");

        enviar.setOnClickListener(
                v -> enviarMensagem()
        );

        entrada.addView(
                enviar,
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.WRAP_CONTENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                )
        );

        tela.addView(
                entrada,
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                )
        );

        // ============================================================
        // ÁREA DA PONTE ALEX V2
        // ============================================================

        TextView tituloPonte = new TextView(this);

        tituloPonte.setText("🌉 Ponte Alex v2");
        tituloPonte.setTextColor(Color.WHITE);
        tituloPonte.setTextSize(19);
        tituloPonte.setPadding(20, 20, 20, 10);

        tela.addView(
                tituloPonte,
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                )
        );

        campoCodigo = new EditText(this);

        campoCodigo.setHint(
                "Cole aqui o código do arquivo..."
        );

        campoCodigo.setHintTextColor(Color.LTGRAY);
        campoCodigo.setTextColor(Color.WHITE);
        campoCodigo.setTextSize(15);
        campoCodigo.setGravity(Gravity.TOP);
        campoCodigo.setMinLines(5);
        campoCodigo.setPadding(20, 20, 20, 20);

        tela.addView(
                campoCodigo,
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        300
                )
        );

        EditText campoInstrucao = new EditText(this);

        campoInstrucao.setHint(
                "O que a Ponte deve fazer?"
        );

        campoInstrucao.setHintTextColor(Color.LTGRAY);
        campoInstrucao.setTextColor(Color.WHITE);
        campoInstrucao.setTextSize(15);
        campoInstrucao.setPadding(20, 15, 20, 15);

        tela.addView(
                campoInstrucao,
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                )
        );

        Button enviarPonte = new Button(this);

        enviarPonte.setText(
                "🌉 Processar pela Ponte"
        );

        enviarPonte.setOnClickListener(
                v -> processarPelaPonte(
                        campoCodigo.getText().toString(),
                        campoInstrucao.getText().toString()
                )
        );

        tela.addView(
                enviarPonte,
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                )
        );

        setContentView(tela);
    }

    // ============================================================
    // ABRIR SELETOR DE ARQUIVO
    // ============================================================

    private void abrirSeletorDeArquivo() {

        Intent intent =
                new Intent(Intent.ACTION_OPEN_DOCUMENT);

        intent.addCategory(
                Intent.CATEGORY_OPENABLE
        );

        intent.setType("*/*");

        startActivityForResult(
                intent,
                REQUEST_SELECIONAR_ARQUIVO
        );
    }

    // ============================================================
    // RESULTADO DO SELETOR DE ARQUIVO
    // ============================================================

    @Override
    protected void onActivityResult(
            int requestCode,
            int resultCode,
            Intent data
    ) {

        super.onActivityResult(
                requestCode,
                resultCode,
                data
        );

        if (
                requestCode != REQUEST_SELECIONAR_ARQUIVO
                        || resultCode != RESULT_OK
                        || data == null
                        || data.getData() == null
        ) {

            return;
        }

        Uri uri = data.getData();

        lerArquivoSelecionado(uri);
    }

    // ============================================================
    // LER ARQUIVO
    // ============================================================

    private void lerArquivoSelecionado(Uri uri) {

        executor.execute(() -> {

            try {

                String nome =
                        obterNomeArquivo(uri);

                if (nome == null || nome.isEmpty()) {
                    nome = "arquivo_selecionado";
                }

                final String nomeFinal = nome;

                // ========================================================
                // ZIP
                // ========================================================

                if (nome.toLowerCase().endsWith(".zip")) {

                    List<String> arquivosZip =
                            listarArquivosZip(uri);

                    boolean encontrouApk = false;

                    for (String arquivo : arquivosZip) {

                        if (
                                arquivo.toLowerCase()
                                        .endsWith(".apk")
                        ) {
                            encontrouApk = true;
                            break;
                        }
                    }

                    final boolean apkEncontrado =
                            encontrouApk;

                    runOnUiThread(() -> {

                        if (arquivosZip.isEmpty()) {

                            adicionarMensagem(
                                    "📦 ZIP carregado: "
                                            + nomeFinal
                                            + "\n"
                                            + "Nenhum arquivo encontrado dentro do ZIP."
                            );

                            return;
                        }

                        StringBuilder lista =
                                new StringBuilder();

                        lista.append(
                                "📦 ZIP carregado: "
                        );

                        lista.append(nomeFinal);

                        lista.append(
                                "\n\nArquivos encontrados:"
                        );

                        for (String arquivo : arquivosZip) {

                            lista.append("\n📄 ");
                            lista.append(arquivo);
                        }

                        if (apkEncontrado) {

                            lista.append(
                                    "\n\n📱 APK encontrado dentro do ZIP!"
                            );

                            lista.append(
                                    "\n📱 Pronto para instalar."
                            );

                        } else {

                            lista.append(
                                    "\n\n📦 Nenhum APK encontrado dentro do ZIP."
                            );
                        }

                        adicionarMensagem(
                                lista.toString()
                        );
                    });

                    // ========================================================
                    // INSTALAR APK ENCONTRADO
                    // ========================================================

                    if (apkEncontrado) {

                        runOnUiThread(() -> {

                            Button botaoInstalar =
                                    new Button(this);

                            botaoInstalar.setText(
                                    "📱 Instalar APK"
                            );

                            botaoInstalar.setOnClickListener(
                                    v -> {

                                        executor.execute(() -> {

                                            try {

                                                extrairEInstalarApk(
                                                        uri
                                                );

                                            } catch (
                                                    Exception erro
                                            ) {

                                                runOnUiThread(() -> {

                                                    adicionarMensagem(
                                                            "📱 Não foi possível instalar o APK: "
                                                                    + erro.getMessage()
                                                    );
                                                });
                                            }
                                        });
                                    }
                            );

                            tela.addView(
                                    botaoInstalar
                            );
                        });
                    }

                    return;
                }

                // ========================================================
                // APK DIRETO
                // ========================================================

                if (nomeFinal.toLowerCase().endsWith(".apk")) {

                    File apkFile =
                            new File(
                                    getCacheDir(),
                                    "apk_direto_instalacao.apk"
                            );

                    InputStream entradaApk =
                            getContentResolver()
                                    .openInputStream(uri);

                    if (entradaApk == null) {

                        throw new Exception(
                                "Não foi possível abrir o APK."
                        );
                    }

                    FileOutputStream saidaApk =
                            new FileOutputStream(
                                    apkFile
                            );

                    byte[] bufferApk =
                            new byte[8192];

                    int quantidadeApk;

                    while (
                            (quantidadeApk =
                                    entradaApk.read(bufferApk))
                                    != -1
                    ) {

                        saidaApk.write(
                                bufferApk,
                                0,
                                quantidadeApk
                        );
                    }

                    saidaApk.flush();
                    saidaApk.close();
                    entradaApk.close();

                    runOnUiThread(() -> {

                        adicionarMensagem(
                                "📱 APK carregado: "
                                        + nomeFinal
                                        + "\n\n"
                                        + "O APK foi reconhecido corretamente."
                                        + "\n"
                                        + "Ele não será lido como texto."
                        );

                        Button botaoInstalar =
                                new Button(this);

                        botaoInstalar.setText(
                                "📱 Instalar APK"
                        );

                        botaoInstalar.setOnClickListener(
                                v -> abrirInstaladorApk(
                                        apkFile
                                )
                        );

                        tela.addView(
                                botaoInstalar
                        );
                    });

                    return;
                }

                // ========================================================
                // ARQUIVO DE TEXTO
                // ========================================================

                String conteudo =
                        lerConteudoArquivo(uri);

                nomeArquivoSelecionado =
                        nomeFinal;

                conteudoArquivoSelecionado =
                        conteudo;

                runOnUiThread(() -> {

                    campoCodigo.setText(
                            conteudoArquivoSelecionado
                    );

                    adicionarMensagem(
                            "📎 Arquivo carregado: "
                                    + nomeArquivoSelecionado
                                    + "\n"
                                    + "Tamanho: "
                                    + conteudoArquivoSelecionado.length()
                                    + " caracteres."
                    );

                    adicionarMensagem(
                            "📎 Arquivo pronto para a próxima etapa."
                    );
                });

                return;

            } catch (Exception erro) {

                runOnUiThread(() -> {

                    adicionarMensagem(
                            "📎 Erro ao ler o arquivo: "
                                    + erro.getMessage()
                    );
                });
            }
        });
    }

    // ============================================================
    // LISTAR ARQUIVOS DO ZIP
    // ============================================================

    private List<String> listarArquivosZip(Uri uri)
            throws Exception {

        List<String> arquivos =
                new ArrayList<>();

        InputStream entrada =
                getContentResolver()
                        .openInputStream(uri);

        if (entrada == null) {
            throw new Exception(
                    "Não foi possível abrir o ZIP."
            );
        }

        ZipInputStream zip =
                new ZipInputStream(
                        entrada
                );

        ZipEntry entradaZip;

        while (
                (entradaZip = zip.getNextEntry())
                        != null
        ) {

            if (!entradaZip.isDirectory()) {

                arquivos.add(
                        entradaZip.getName()
                );
            }

            zip.closeEntry();
        }
                
        zip.close();
        entrada.close();

        return arquivos;
    }

    // ============================================================
    // EXTRAIR E INSTALAR APK
    // ============================================================

    private void extrairEInstalarApk(Uri uri)
            throws Exception {

        InputStream entrada =
                getContentResolver()
                        .openInputStream(uri);

        if (entrada == null) {
            throw new Exception(
                    "Não foi possível abrir o ZIP."
            );
        }

        ZipInputStream zip =
                new ZipInputStream(entrada);

        ZipEntry entradaZip;

        while (
                (entradaZip = zip.getNextEntry())
                        != null
        ) {

            if (
                    !entradaZip.isDirectory()
                            &&
                    entradaZip.getName()
                            .toLowerCase()
                            .endsWith(".apk")
            ) {

                File apkFile =
                        new File(
                                getCacheDir(),
                                "apk_instalacao.apk"
                        );

                FileOutputStream saida =
                        new FileOutputStream(
                                apkFile
                        );

                byte[] buffer =
                        new byte[8192];

                int quantidade;

                while (
                        (quantidade = zip.read(buffer))
                                != -1
                ) {

                    saida.write(
                            buffer,
                            0,
                            quantidade
                    );
                }

                saida.flush();
                saida.close();

                zip.closeEntry();
                zip.close();
                entrada.close();

                abrirInstaladorApk(apkFile);

                return;
            }

            zip.closeEntry();
        }

        zip.close();
        entrada.close();

        throw new Exception(
                "Nenhum APK foi encontrado dentro do ZIP."
        );
    }

    // ============================================================
    // ABRIR INSTALADOR DO APK
    // ============================================================

    private void abrirInstaladorApk(File apkFile) {

        try {

            if (
                    Build.VERSION.SDK_INT >=
                            Build.VERSION_CODES.O
            ) {

                if (
                        !getPackageManager()
                                .canRequestPackageInstalls()
                ) {

                    Intent configuracao =
                            new Intent(
                                    Settings
                                            .ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                                    Uri.parse(
                                            "package:"
                                                    + getPackageName()
                                    )
                            );

                    startActivity(
                            configuracao
                    );

                    adicionarMensagem(
                            "📱 Permita a instalação deste aplicativo e depois tente instalar o APK novamente."
                    );

                    return;
                }
            }

            Uri apkUri =
                    FileProvider.getUriForFile(
                            this,
                            getPackageName()
                                    + ".fileprovider",
                            apkFile
                    );

            Intent instalador =
                    new Intent(
                            Intent.ACTION_VIEW
                    );

            instalador.setDataAndType(
                    apkUri,
                    "application/vnd.android.package-archive"
            );

            instalador.addFlags(
                    Intent.FLAG_GRANT_READ_URI_PERMISSION
            );

            instalador.addFlags(
                    Intent.FLAG_ACTIVITY_NEW_TASK
            );

            startActivity(
                    instalador
            );

        } catch (
                ActivityNotFoundException erro
        ) {

            adicionarMensagem(
                    "📱 Não foi possível abrir o instalador do APK."
            );

        } catch (Exception erro) {

            adicionarMensagem(
                    "📱 Erro ao abrir o APK: "
                            + erro.getMessage()
            );
        }
    }

    // ============================================================
    // OBTER NOME DO ARQUIVO
    // ============================================================

    private String obterNomeArquivo(Uri uri) {

        Cursor cursor = null;

        try {

            cursor =
                    getContentResolver().query(
                            uri,
                            null,
                            null,
                            null,
                            null
                    );

            if (
                    cursor != null
                            && cursor.moveToFirst()
            ) {

                int indice =
                        cursor.getColumnIndex(
                                OpenableColumns.DISPLAY_NAME
                        );

                if (indice >= 0) {

                    return cursor.getString(
                            indice
                    );
                }
            }

        } finally {

            if (cursor != null) {
                cursor.close();
            }
        }

        return "";
    }

    // ============================================================
    // LER CONTEÚDO UTF-8
    // ============================================================

    private String lerConteudoArquivo(Uri uri)
            throws Exception {

        InputStream entrada =
                getContentResolver()
                        .openInputStream(uri);

        if (entrada == null) {
            throw new Exception(
                    "Não foi possível abrir o arquivo."
            );
        }

        StringBuilder resultado =
                new StringBuilder();

        BufferedReader leitor =
                new BufferedReader(
                        new InputStreamReader(
                                entrada,
                                StandardCharsets.UTF_8
                        )
                );

        String linha;

        while (
                (linha = leitor.readLine())
                        != null
        ) {

            resultado
                    .append(linha)
                    .append("\n");
        }

        leitor.close();
        entrada.close();

        return resultado.toString();
    }

    // ============================================================
    // ENVIAR MENSAGEM PARA A API
    // ============================================================
    // ENVIAR MENSAGEM PARA A API
    // ============================================================

    private void enviarMensagem() {

        String texto =
                campoMensagem.getText()
                        .toString()
                        .trim();

        if (texto.isEmpty()) {
            return;
        }

        adicionarMensagem(
                "Você: " + texto
        );

        campoMensagem.setText("");

        adicionarMensagem(
                "Alex: pensando..."
        );

        executor.execute(() -> {

            try {

                JSONObject pedido =
                        new JSONObject();

                JSONArray arrayHistorico =
                        new JSONArray();

                for (JSONObject item : historico) {
                    arrayHistorico.put(item);
                }

                pedido.put(
                        "pergunta",
                        texto
                );

                pedido.put(
                        "historico",
                        arrayHistorico
                );

                pedido.put(
                        "contexto_arquivo",
                        conteudoArquivoSelecionado
                );

                pedido.put(
                        "nome_arquivo",
                        nomeArquivoSelecionado
                );

                URL url =
                        new URL(API_URL);

                HttpURLConnection conexao =
                       (HttpURLConnection)
                                url.openConnection();

                conexao.setRequestMethod("POST");

                conexao.setRequestProperty(
                        "Content-Type",
                        "application/json"
                );

                conexao.setRequestProperty(
                        "Accept",
                        "application/json"
                );

                conexao.setDoOutput(true);

                conexao.setConnectTimeout(
                        30000
                );

                conexao.setReadTimeout(
                        60000
                );

                byte[] dados =
                        pedido.toString()
                                .getBytes(
                                       StandardCharsets.UTF_8
                                );

                try (
                        OutputStream saida =
                                conexao.getOutputStream()
                ) {

                    saida.write(dados);
                }

                int codigo =
                        conexao.getResponseCode();

                InputStream entradaResposta;

                if (
                        codigo >= 200
                                && codigo < 300
                ) {

                    entradaResposta =
                            conexao.getInputStream();

                } else {

                    entradaResposta =
                            conexao.getErrorStream();
                }

                String respostaTexto =
                        lerResposta(
                                entradaResposta
                        );

                conexao.disconnect();

                JSONObject resposta =
                        new JSONObject(
                                respostaTexto
                        );

                boolean sucesso =
                        resposta.optBoolean(
                                "success",
                                false
                       );

                String respostaAlex =
                        resposta.optString(
                                "resposta",
                                "Não consegui obter uma resposta."
                        );

                if (sucesso) {

                    JSONObject mensagemUsuario =
                            new JSONObject();

                    mensagemUsuario.put(
                            "role",
                            "user"
                    );

                    mensagemUsuario.put(
                            "content",
                            texto
                    );

                    JSONObject mensagemAlex =
                            new JSONObject();

                    mensagemAlex.put(
                            "role",
                            "model"
                    );

                    mensagemAlex.put(
                            "content",
                            respostaAlex
                    );

                    historico.add(
                            mensagemUsuario
                    );

                    historico.add(
                            mensagemAlex
                    );
                }

                runOnUiThread(() -> {

                    removerMensagemPensando();

                    adicionarMensagem(
                            "Alex: " + respostaAlex
                    );
                });

            } catch (Exception erro) {

                runOnUiThread(() -> {

                    removerMensagemPensando();

                    adicionarMensagem(
                            "Alex: Não consegui conectar "
                                    + "ao servidor agora."
                    );
                });
            }
        });
    }  
    // ============================================================
    // LER RESPOSTA DO SERVIDOR
    // ============================================================

    private String lerResposta(
            InputStream entrada
    ) throws Exception {

        if (entrada == null) {

            return "{\"success\":false,"
                    + "\"resposta\":\"Resposta vazia do servidor.\"}";
        }

        StringBuilder resultado =
                new StringBuilder();

        BufferedReader leitor =
                new BufferedReader(
                        new InputStreamReader(
                                entrada,
                                StandardCharsets.UTF_8
                        )
                );

        String linha;

        while (
                (linha = leitor.readLine())
                        != null
        ) {

            resultado.append(linha);
        }

        leitor.close();

        return resultado.toString();
    }

    // ============================================================
    // PROCESSAR CÓDIGO PELA PONTE ALEX V2
    // ============================================================

    private void processarPelaPonte(
            String codigo,
            String instrucao
    ) {

        codigo = codigo.trim();
        instrucao = instrucao.trim();

        if (codigo.isEmpty()) {

            adicionarMensagem(
                    "Ponte: cole um código para processar."
            );

            return;
        }

        if (instrucao.isEmpty()) {

            adicionarMensagem(
                    "Ponte: informe o que deseja modificar."
            );

            return;
        }

        adicionarMensagem(
                "Você → Ponte: processando..."
        );

        final String codigoFinal = codigo;
        final String instrucaoFinal = instrucao;

        executor.execute(() -> {

            HttpURLConnection conexao = null;

            try {

                JSONObject pedido =
                        new JSONObject();

                pedido.put(
                        "fileContent",
                        codigoFinal
                );

                pedido.put(
                        "instruction",
                        instrucaoFinal
                );

                pedido.put(
                        "filename",
                        "script_alex.py"
                );

                pedido.put(
                        "outputFilename",
                        JSONObject.NULL
                );

                pedido.put(
                        "searchTarget",
                        JSONObject.NULL
                );

                pedido.put(
                        "replaceWith",
                        JSONObject.NULL
                );

                URL url =
                        new URL(PONTE_API_URL);

                conexao =
                        (HttpURLConnection)
                                url.openConnection();

                conexao.setRequestMethod("POST");

                conexao.setRequestProperty(
                        "Content-Type",
                        "application/json"
                );

                conexao.setRequestProperty(
                        "Accept",
                        "application/json"
                );

                conexao.setDoOutput(true);

                conexao.setConnectTimeout(
                        30000
                );

                conexao.setReadTimeout(
                        90000
                );

                byte[] dados =
                        pedido.toString()
                                .getBytes(
                                        StandardCharsets.UTF_8
                                );

                try (
                        OutputStream saida =
                                conexao.getOutputStream()
                ) {

                    saida.write(dados);
                }

                int codigoHttp =
                        conexao.getResponseCode();

                InputStream entradaResposta;

                if (
                        codigoHttp >= 200
                                && codigoHttp < 300
                ) {

                    entradaResposta =
                            conexao.getInputStream();

                } else {

                    entradaResposta =
                            conexao.getErrorStream();
                }

                String respostaTexto =
                        lerResposta(
                                entradaResposta
                        );

                JSONObject resposta =
                        new JSONObject(
                                respostaTexto
                        );

                boolean sucesso =
                        resposta.optBoolean(
                                "success",
                                false
                        );

                if (sucesso) {

                    JSONObject arquivo =
                            resposta.optJSONObject(
                                    "processedFile"
                            );

                    String nomeArquivo =
                            arquivo != null
                                    ? arquivo.optString(
                                            "filename",
                                            ""
                                    )
                                    : "";

                    String download =
                            arquivo != null
                                    ? arquivo.optString(
                                            "downloadUrl",
                                            ""
                                    )
                                    : "";

                    String status =
                            resposta.optString(
                                    "status",
                                    "PROCESSADO"
                            );

                    runOnUiThread(() -> {

                        adicionarMensagem(
                                "Ponte: " + status
                                        + "\nArquivo processado: "
                                        + nomeArquivo
                        );

                        if (!download.isEmpty()) {

                            Button botaoDownload =
                                    new Button(this);

                            botaoDownload.setText(
                                    "📥 Baixar arquivo processado"
                            );

                            botaoDownload.setOnClickListener(
                                    v -> {

                                        try {

                                            String urlDownload =
                                                    download;

                                            if (
                                                    !urlDownload.startsWith(
                                                            "http://"
                                                    )
                                                    &&
                                                    !urlDownload.startsWith(
                                                            "https://"
                                                    )
                                            ) {

                                                urlDownload =
                                                        "https://ponte-alex-v2.onrender.com"
                                                                + (
                                                                    urlDownload.startsWith("/")
                                                                            ? urlDownload
                                                                            : "/" + urlDownload
                                                                );
                                            }

                                            Intent navegador =
                                                    new Intent(
                                                            Intent.ACTION_VIEW,
                                                            Uri.parse(
                                                                    urlDownload
                                                            )
                                                    );

                                            startActivity(
                                                    navegador
                                            );

                                        } catch (Exception erro) {

                                            adicionarMensagem(
                                                    "📥 Não foi possível abrir o download: "
                                                            + erro.getMessage()
                                            );
                                        }
                                    }
                            );

                            tela.addView(
                                    botaoDownload,
                                    new LinearLayout.LayoutParams(
                                            ViewGroup.LayoutParams.MATCH_PARENT,
                                            ViewGroup.LayoutParams.WRAP_CONTENT
                                    )
                            );
                        }
                    });

                } else {

                    String erro =
                            resposta.optString(
                                    "error",
                                    resposta.optString(
                                            "resposta",
                                            "A Ponte não conseguiu processar."
                                    )
                            );

                    runOnUiThread(() -> {

                        adicionarMensagem(
                                "Ponte: " + erro
                        );
                    });
                }

            } catch (Exception erro) {

                runOnUiThread(() -> {

                    adicionarMensagem(
                            "Ponte: não foi possível "
                                    + "conectar ao servidor."
                    );
                });

            } finally {

                if (conexao != null) {
                    conexao.disconnect();
                }
            }
        });
    }

    // ============================================================
    // MENSAGEM "PENSANDO..."
    // ============================================================

    private void removerMensagemPensando() {

        int quantidade =
                mensagens.getChildCount();

        if (quantidade == 0) {
            return;
        }

        View ultima =
                mensagens.getChildAt(
                        quantidade - 1
                );

        if (ultima instanceof TextView) {

            TextView texto =
                    (TextView) ultima;

            String valor =
                    texto.getText().toString();

            if (
                    valor.equals(
                            "Alex: pensando..."
                    )
            ) {

                mensagens.removeView(
                        ultima
                );
            }
        }
    }

    // ============================================================
    // ADICIONAR MENSAGEM NA TELA
    // ============================================================

    private void adicionarMensagem(
            String texto
    ) {

        TextView mensagem =
                new TextView(this);

        mensagem.setText(texto);
        mensagem.setTextColor(Color.WHITE);
        mensagem.setTextSize(16);

        mensagem.setPadding(
                20,
                15,
                20,
                15
        );

        mensagens.addView(
                mensagem
        );
    }

    @Override
    protected void onDestroy() {

        executor.shutdownNow();

        super.onDestroy();
    }

    @Override
    public void onBackPressed() {
        super.onBackPressed();
    }
   }

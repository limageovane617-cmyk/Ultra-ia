package com.geovani.alexiaultra;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.PopupWindow;
import android.widget.ScrollView;
import android.widget.TextView;

import androidx.core.content.FileProvider;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
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

    private FrameLayout raiz;

    private LinearLayout tela;
    private LinearLayout mensagens;

    private ScrollView scrollChat;

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

    // ============================================================
    // APIs
    // ============================================================

    private static final String API_URL =
            "https://ultra-ia-pro.onrender.com/api/chat";

    private static final String PONTE_API_URL =
            "https://ultra-ia-pro.onrender.com/api/ponte/processar";

    // ============================================================
    // CICLO DA ACTIVITY
    // ============================================================

    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);

        // ========================================================
        // CORREÇÃO DO TECLADO
        // ========================================================

        getWindow().setSoftInputMode(
                WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE
        );

        criarInterface();
    }

    // ============================================================
    // CONVERTER DP
    // ============================================================

    private int dp(float valor) {

        return (int) (
                valor
                        * getResources()
                        .getDisplayMetrics()
                        .density
        );
    }

    // ============================================================
    // CRIAR INTERFACE
    // ============================================================

    private void criarInterface() {

        // ========================================================
        // RAIZ
        // ========================================================

        raiz =
                new FrameLayout(this);

        raiz.setBackgroundColor(
                Color.BLACK
        );

        // ========================================================
        // FUNDO BASE DA ULTRA
        // ========================================================

        ImageView fundo =
                new ImageView(this);

        fundo.setScaleType(
                ImageView.ScaleType.CENTER_CROP
        );

        fundo.setImageResource(
                R.drawable.fundo_ultra
        );

        raiz.addView(
                fundo,
                new FrameLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.MATCH_PARENT
                )
        );

        // ========================================================
        // CIDADE DA ULTRA
        // ========================================================
        // A cidade fica em uma camada separada.
        // O arquivo cidade_ultra.xml controla a aparência
        // e utiliza cidade_ultra_imagem.png.
        // ========================================================

        ImageView cidade =
                new ImageView(this);

        cidade.setScaleType(
                ImageView.ScaleType.CENTER_CROP
        );

        cidade.setImageResource(
                R.drawable.cidade_ultra
        );

        cidade.setAlpha(
                1.0f
        );

        raiz.addView(
                cidade,
                new FrameLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.MATCH_PARENT
                )
        );

        // ========================================================
        // TELA PRINCIPAL
        // ========================================================

        tela =
                new LinearLayout(this);

        tela.setOrientation(
                LinearLayout.VERTICAL
        );

        tela.setBackgroundColor(
                Color.TRANSPARENT
        );

        raiz.addView(
                tela,
                new FrameLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.MATCH_PARENT
                )
        );

        // ========================================================
        // ÁREA DO CHAT
        // ========================================================

        scrollChat =
                new ScrollView(this);

        scrollChat.setFillViewport(
                true
        );

        scrollChat.setClipToPadding(
                false
        );

        scrollChat.setBackgroundColor(
                Color.TRANSPARENT
        );

        mensagens =
                new LinearLayout(this);

        mensagens.setOrientation(
                LinearLayout.VERTICAL
        );

        mensagens.setPadding(
                dp(14),
                dp(20),
                dp(14),
                dp(20)
        );

        mensagens.setBackgroundColor(
                Color.TRANSPARENT
        );

        scrollChat.addView(
                mensagens,
                new ScrollView.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                )
        );

        // ========================================================
        // IMPORTANTE:
        // A ÁREA DO CHAT OCUPA TODO O ESPAÇO DISPONÍVEL
        // ========================================================

        tela.addView(
                scrollChat,
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        0,
                        1
                )
        );

        // ========================================================
        // ÁREA DE DIGITAÇÃO
        // ========================================================

        LinearLayout entrada =
                new LinearLayout(this);

        entrada.setOrientation(
                LinearLayout.HORIZONTAL
        );

        entrada.setGravity(
                Gravity.CENTER_VERTICAL
        );

        GradientDrawable fundoEntrada =
                new GradientDrawable();

        fundoEntrada.setColor(
                Color.argb(
                        145,
                        15,
                        20,
                        30
                )
        );

        fundoEntrada.setCornerRadius(
                dp(40)
        );

        fundoEntrada.setStroke(
                dp(1),
                Color.argb(
                        70,
                        255,
                        255,
                        255
                )
        );

        entrada.setBackground(
                fundoEntrada
        );

        entrada.setPadding(
                dp(8),
                dp(5),
                dp(7),
                dp(5)
        );

        // ========================================================
        // BOTÃO +
        // ========================================================

        Button botaoMais =
                new Button(this);

        botaoMais.setText(
                "＋"
        );

        botaoMais.setTextSize(
                27
        );

        botaoMais.setTextColor(
                Color.WHITE
        );

        botaoMais.setBackgroundColor(
                Color.TRANSPARENT
        );

        botaoMais.setMinWidth(
                0
        );

        botaoMais.setMinimumWidth(
                0
        );

        botaoMais.setPadding(
                dp(3),
                0,
                dp(3),
                0
        );

        botaoMais.setOnClickListener(
                v -> mostrarMenuFerramentas()
        );

        entrada.addView(
                botaoMais,
                new LinearLayout.LayoutParams(
                        dp(52),
                        ViewGroup.LayoutParams.MATCH_PARENT
                )
        );

        // ========================================================
        // CAMPO DE MENSAGEM
        // ========================================================

        campoMensagem =
                new EditText(this);

        campoMensagem.setHint(
                "Digite sua mensagem..."
        );

        campoMensagem.setHintTextColor(
                Color.argb(
                        190,
                        220,
                        225,
                        235
                )
        );

        campoMensagem.setTextColor(
                Color.WHITE
        );

        campoMensagem.setTextSize(
                16
        );

        campoMensagem.setSingleLine(
                true
        );

        campoMensagem.setBackgroundColor(
                Color.TRANSPARENT
        );

        campoMensagem.setPadding(
                dp(5),
                0,
                dp(5),
                0
        );

        entrada.addView(
                campoMensagem,
                new LinearLayout.LayoutParams(
                        0,
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        1
                )
        );

        // ========================================================
        // BOTÃO ENVIAR
        // ========================================================

        Button enviar =
                new Button(this);

        enviar.setText(
                "🚀"
        );

        enviar.setTextSize(
                20
        );

        enviar.setTextColor(
                Color.WHITE
        );

        enviar.setBackgroundColor(
                Color.TRANSPARENT
        );

        enviar.setMinWidth(
                0
        );

        enviar.setMinimumWidth(
                0
        );

        enviar.setPadding(
                dp(4),
                0,
                dp(3),
                0
        );

        enviar.setOnClickListener(
                v -> enviarMensagem()
        );

        entrada.addView(
                enviar,
                new LinearLayout.LayoutParams(
                        dp(52),
                        ViewGroup.LayoutParams.MATCH_PARENT
                )
        );

        // ========================================================
        // BALÃO DE ENTRADA
        // ========================================================

        LinearLayout.LayoutParams parametrosEntrada =
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        dp(58)
                );

        parametrosEntrada.setMargins(
                dp(12),
                dp(8),
                dp(12),
                dp(12)
        );

        tela.addView(
                entrada,
                parametrosEntrada
        );

        // ========================================================
        // FINALIZAR
        // ========================================================

        setContentView(
                raiz
        );
    }

    // ============================================================
    // MENU DE FERRAMENTAS TRANSLÚCIDO
    // ============================================================

    private void mostrarMenuFerramentas() {

        LinearLayout menuLayout =
                new LinearLayout(this);

        menuLayout.setOrientation(
                LinearLayout.VERTICAL
        );

        menuLayout.setPadding(
                dp(8),
                dp(8),
                dp(8),
                dp(8)
        );

        GradientDrawable fundoMenu =
                new GradientDrawable();

        fundoMenu.setColor(
                Color.argb(
                        185,
                        15,
                        18,
                        27
                )
        );

        fundoMenu.setCornerRadius(
                dp(18)
        );

        fundoMenu.setStroke(
                dp(1),
                Color.argb(
                        75,
                        255,
                        255,
                        255
                )
        );

        menuLayout.setBackground(
                fundoMenu
        );

        String[] ferramentas = {

                "🖼️  Imagem",
                "🎬  Vídeo",
                "🔊  Voz",
                "💻  Código",
                "📎  Arquivo",
                "🎭  Personagem",
                "🧠  Memória",
                "🗑️  Limpar chat"
        };

        PopupWindow[] janela =
                new PopupWindow[1];

        for (
                String ferramenta :
                ferramentas
        ) {

            TextView item =
                    new TextView(this);

            item.setText(
                    ferramenta
            );

            item.setTextColor(
                    Color.WHITE
            );

            item.setTextSize(
                    16
            );

            item.setGravity(
                    Gravity.CENTER_VERTICAL
            );

            item.setPadding(
                    dp(14),
                    dp(13),
                    dp(14),
                    dp(13)
            );

            item.setBackgroundColor(
                    Color.TRANSPARENT
            );

            item.setOnClickListener(
                    v -> {

                        String selecionada =
                                ferramenta.trim();

                        if (
                                janela[0] != null
                        ) {

                            janela[0].dismiss();
                        }

                        executarFerramenta(
                                selecionada
                        );
                    }
            );

            menuLayout.addView(
                    item,
                    new LinearLayout.LayoutParams(
                            ViewGroup.LayoutParams.MATCH_PARENT,
                            dp(52)
                    )
            );
        }

        PopupWindow popup =
                new PopupWindow(
                        menuLayout,
                        dp(285),
                        ViewGroup.LayoutParams.WRAP_CONTENT,
                        true
                );

        janela[0] =
                popup;

        popup.setBackgroundDrawable(
                new ColorDrawable(
                        Color.TRANSPARENT
                )
        );

        popup.setOutsideTouchable(
                true
        );

        popup.setElevation(
                dp(12)
        );

        popup.setAnimationStyle(
                android.R.style.Animation_Dialog
        );

        // ========================================================
        // COLOCAR O MENU ACIMA DO CAMPO DE DIGITAÇÃO
        // ========================================================

        popup.showAtLocation(
                raiz,
                Gravity.BOTTOM | Gravity.START,
                dp(16),
                dp(78)
        );
    }

    // ============================================================
    // EXECUTAR FERRAMENTA
    // ============================================================

    private void executarFerramenta(
            String ferramenta
    ) {

        if (
                ferramenta.equals(
                        "🖼️  Imagem"
                )
        ) {

            campoMensagem.setHint(
                    "Descreva a imagem que você quer criar..."
            );

            campoMensagem.requestFocus();

            adicionarMensagem(
                    "🖼️ Modo Imagem ativado.\n\n"
                            + "Digite a descrição da imagem que você quer gerar."
            );

            return;
        }

        if (
                ferramenta.equals(
                        "💻  Código"
                )
        ) {

            mostrarInterfaceCodigo();

            return;
        }

        if (
                ferramenta.equals(
                        "📎  Arquivo"
                )
        ) {

            abrirSeletorDeArquivo();

            return;
        }

        if (
                ferramenta.equals(
                        "🗑️  Limpar chat"
                )
        ) {

            mensagens.removeAllViews();

            adicionarMensagem(
                    "🗑️ Chat limpo."
            );

            return;
        }

        adicionarMensagem(
                "🧰 Ferramenta selecionada: "
                        + ferramenta
        );
    }

    // ============================================================
    // INTERFACE DE CÓDIGO
    // ============================================================

    private void mostrarInterfaceCodigo() {

        LinearLayout layout =
                new LinearLayout(this);

        layout.setOrientation(
                LinearLayout.VERTICAL
        );

        layout.setPadding(
                dp(20),
                dp(10),
                dp(20),
                dp(10)
        );

        campoCodigo =
                new EditText(this);

        campoCodigo.setHint(
                "Cole aqui o código..."
        );

        campoCodigo.setHintTextColor(
                Color.LTGRAY
        );

        campoCodigo.setTextColor(
                Color.WHITE
        );

        campoCodigo.setTextSize(
                15
        );

        campoCodigo.setGravity(
                Gravity.TOP
        );

        campoCodigo.setMinLines(
                8
        );

        campoCodigo.setPadding(
                dp(15),
                dp(15),
                dp(15),
                dp(15)
        );

        GradientDrawable fundoCodigo =
                new GradientDrawable();

        fundoCodigo.setColor(
                Color.argb(
                        190,
                        20,
                        26,
                        38
                )
        );

        fundoCodigo.setCornerRadius(
                dp(22)
        );

        fundoCodigo.setStroke(
                dp(1),
                Color.argb(
                        80,
                        255,
                        255,
                        255
                )
        );

        campoCodigo.setBackground(
                fundoCodigo
        );

        layout.addView(
                campoCodigo,
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        0,
                        1
                )
        );

        // ========================================================
        // INSTRUÇÃO
        // ========================================================

        EditText campoInstrucao =
                new EditText(this);

        campoInstrucao.setHint(
                "O que a Ponte deve fazer?"
        );

        campoInstrucao.setHintTextColor(
                Color.LTGRAY
        );

        campoInstrucao.setTextColor(
                Color.WHITE
        );

        campoInstrucao.setTextSize(
                15
        );

        campoInstrucao.setPadding(
                dp(15),
                dp(15),
                dp(15),
                dp(15)
        );

        GradientDrawable fundoInstrucao =
                new GradientDrawable();

        fundoInstrucao.setColor(
                Color.argb(
                        190,
                        20,
                        26,
                        38
                )
        );

        fundoInstrucao.setCornerRadius(
                dp(22)
        );

        fundoInstrucao.setStroke(
                dp(1),
                Color.argb(
                        80,
                        255,
                        255,
                        255
                )
        );

        campoInstrucao.setBackground(
                fundoInstrucao
        );

        LinearLayout.LayoutParams parametrosInstrucao =
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                );

        parametrosInstrucao.setMargins(
                0,
                dp(12),
                0,
                0
        );

        layout.addView(
                campoInstrucao,
                parametrosInstrucao
        );

        AlertDialog dialog =
                new AlertDialog.Builder(this)
                        .setTitle(
                                "💻 Código"
                        )
                        .setView(
                                layout
                        )
                        .setNegativeButton(
                                "Cancelar",
                                null
                        )
                        .setPositiveButton(
                                "🌉 Processar",
                                null
                        )
                        .create();

        dialog.setOnShowListener(
                dialogInterface -> {

                    Button botaoProcessar =
                            dialog.getButton(
                                    AlertDialog.BUTTON_POSITIVE
                            );

                    botaoProcessar.setOnClickListener(
                            v -> {

                                String codigo =
                                        campoCodigo
                                                .getText()
                                                .toString();

                                String instrucao =
                                        campoInstrucao
                                                .getText()
                                                .toString();

                                processarPelaPonte(
                                        codigo,
                                        instrucao
                                );

                                dialog.dismiss();
                            }
                    );
                }
        );

        dialog.show();
    }

    // ============================================================
    // ABRIR SELETOR DE ARQUIVO
    // ============================================================

    private void abrirSeletorDeArquivo() {

        Intent intent =
                new Intent(
                        Intent.ACTION_OPEN_DOCUMENT
                );

        intent.addCategory(
                Intent.CATEGORY_OPENABLE
        );

        intent.setType(
                "*/*"
        );

        startActivityForResult(
                intent,
                REQUEST_SELECIONAR_ARQUIVO
        );
    }

    // ============================================================
    // RESULTADO DO SELETOR
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
                requestCode
                        != REQUEST_SELECIONAR_ARQUIVO
                        || resultCode
                        != RESULT_OK
                        || data == null
                        || data.getData() == null
        ) {

            return;
        }

        Uri uri =
                data.getData();

        lerArquivoSelecionado(
                uri
        );
    }

    // ============================================================
    // LER ARQUIVO
    // ============================================================

    private void lerArquivoSelecionado(
            Uri uri
    ) {

        executor.execute(
                () -> {

                    try {

                        String nome =
                                obterNomeArquivo(
                                        uri
                                );

                        if (
                                nome == null
                                        || nome.isEmpty()
                        ) {

                            nome =
                                    "arquivo_selecionado";
                        }

                        final String nomeFinal =
                                nome;

                        // ====================================================
                        // ZIP
                        // ====================================================

                        if (
                                nome.toLowerCase()
                                        .endsWith(".zip")
                        ) {

                            List<String> arquivosZip =
                                    listarArquivosZip(
                                            uri
                                    );

                            boolean encontrouApk =
                                    false;

                            for (
                                    String arquivo :
                                    arquivosZip
                            ) {

                                if (
                                        arquivo
                                                .toLowerCase()
                                                .endsWith(".apk")
                                ) {

                                    encontrouApk =
                                            true;

                                    break;
                                }
                            }

                            final boolean apkEncontrado =
                                    encontrouApk;

                            runOnUiThread(
                                    () -> {

                                        if (
                                                arquivosZip.isEmpty()
                                        ) {

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

                                        lista.append(
                                                nomeFinal
                                        );

                                        lista.append(
                                                "\n\nArquivos encontrados:"
                                        );

                                        for (
                                                String arquivo :
                                                arquivosZip
                                        ) {

                                            lista.append(
                                                    "\n📄 "
                                            );

                                            lista.append(
                                                    arquivo
                                            );
                                        }

                                        if (
                                                apkEncontrado
                                        ) {

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
                                    }
                            );

                            // ====================================================
                            // INSTALAR APK
                            // ====================================================

                            if (
                                    apkEncontrado
                            ) {

                                runOnUiThread(
                                        () -> {

                                            Button botaoInstalar =
                                                    criarBotaoAcao(
                                                            "📱 Instalar APK"
                                                    );

                                            botaoInstalar.setOnClickListener(
                                                    v -> {

                                                        executor.execute(
                                                                () -> {

                                                                    try {

                                                                        extrairEInstalarApk(
                                                                                uri
                                                                        );

                                                                    } catch (
                                                                            Exception erro
                                                                    ) {

                                                                        runOnUiThread(
                                                                                () -> {

                                                                                    adicionarMensagem(
                                                                                            "📱 Não foi possível instalar o APK: "
                                                                                                    + erro.getMessage()
                                                                                    );
                                                                                }
                                                                        );
                                                                    }
                                                                }
                                                        );
                                                    }
                                            );

                                            adicionarBotaoAoChat(
                                                    botaoInstalar
                                            );
                                        }
                                );
                            }

                            return;
                        }

                        // ====================================================
                        // APK DIRETO
                        // ====================================================

                        if (
                                nomeFinal
                                        .toLowerCase()
                                        .endsWith(".apk")
                        ) {

                            File apkFile =
                                    new File(
                                            getCacheDir(),
                                            "apk_direto_instalacao.apk"
                                    );

                            InputStream entradaApk =
                                    getContentResolver()
                                            .openInputStream(
                                                    uri
                                            );

                            if (
                                    entradaApk == null
                            ) {

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
                                    (
                                            quantidadeApk =
                                                    entradaApk.read(
                                                            bufferApk
                                                    )
                                    )
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

                            runOnUiThread(
                                    () -> {

                                        adicionarMensagem(
                                                "📱 APK carregado: "
                                                        + nomeFinal
                                                        + "\n\n"
                                                        + "O APK foi reconhecido corretamente."
                                                        + "\n"
                                                        + "Ele não será lido como texto."
                                        );

                                        Button botaoInstalar =
                                                criarBotaoAcao(
                                                        "📱 Instalar APK"
                                                );

                                        botaoInstalar.setOnClickListener(
                                                v -> abrirInstaladorApk(
                                                        apkFile
                                                )
                                        );

                                        adicionarBotaoAoChat(
                                                botaoInstalar
                                        );
                                    }
                            );

                            return;
                        }

                        // ====================================================
                        // ARQUIVO DE TEXTO
                        // ====================================================

                        String conteudo =
                                lerConteudoArquivo(
                                        uri
                                );

                        nomeArquivoSelecionado =
                                nomeFinal;

                        conteudoArquivoSelecionado =
                                conteudo;

                        runOnUiThread(
                                () -> {

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
                                }
                        );

                    } catch (
                            Exception erro
                    ) {

                        runOnUiThread(
                                () -> {

                                    adicionarMensagem(
                                            "📎 Erro ao ler o arquivo: "
                                                    + erro.getMessage()
                                    );
                                }
                        );
                    }
                }
        );
    }

    // ============================================================
    // LISTAR ARQUIVOS ZIP
    // ============================================================

    private List<String> listarArquivosZip(
            Uri uri
    ) throws Exception {

        List<String> arquivos =
                new ArrayList<>();

        InputStream entrada =
                getContentResolver()
                        .openInputStream(
                                uri
                        );

        if (
                entrada == null
        ) {

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
                (
                        entradaZip =
                                zip.getNextEntry()
                )
                        != null
        ) {

            if (
                    !entradaZip.isDirectory()
            ) {

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

    private void extrairEInstalarApk(
            Uri uri
    ) throws Exception {

        InputStream entrada =
                getContentResolver()
                        .openInputStream(
                                uri
                        );

        if (
                entrada == null
        ) {

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
                (
                        entradaZip =
                                zip.getNextEntry()
                )
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
                        (
                                quantidade =
                                        zip.read(
                                                buffer
                                        )
                                )
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

                abrirInstaladorApk(
                        apkFile
                );

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
    // INSTALADOR APK
    // ============================================================

    private void abrirInstaladorApk(
            File apkFile
    ) {

        try {

            if (
                    Build.VERSION.SDK_INT
                            >= Build.VERSION_CODES.O
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

        } catch (
                Exception erro
        ) {

            adicionarMensagem(
                    "📱 Erro ao abrir o APK: "
                            + erro.getMessage()
            );
        }
    }

    // ============================================================
    // NOME DO ARQUIVO
    // ============================================================

    private String obterNomeArquivo(
            Uri uri
    ) {

        Cursor cursor =
                null;

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

                if (
                        indice >= 0
                ) {

                    return cursor.getString(
                            indice
                    );
                }
            }

        } finally {

            if (
                    cursor != null
            ) {

                cursor.close();
            }
        }

        return "";
    }

    // ============================================================
    // LER ARQUIVO UTF-8
    // ============================================================

    private String lerConteudoArquivo(
            Uri uri
    ) throws Exception {

        InputStream entrada =
                getContentResolver()
                        .openInputStream(
                                uri
                        );

        if (
                entrada == null
        ) {

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
                (
                        linha =
                                leitor.readLine()
                )
                        != null
        ) {

            resultado
                    .append(
                            linha
                    )
                    .append(
                            "\n"
                    );
        }

        leitor.close();
        entrada.close();

        return resultado.toString();
    }

    // ============================================================
    // ENVIAR MENSAGEM
    // ============================================================

    private void enviarMensagem() {

        String texto =
                campoMensagem
                        .getText()
                        .toString()
                        .trim();

        if (
                texto.isEmpty()
        ) {

            return;
        }

        adicionarMensagem(
                "Você: " + texto
        );

        campoMensagem.setText(
                ""
        );

        campoMensagem.setHint(
                "Digite sua mensagem..."
        );

        adicionarMensagem(
                "Alex: pensando..."
        );

        executor.execute(
                () -> {

                    HttpURLConnection connection =
                            null;

                    try {

                        JSONObject pedido =
                                new JSONObject();

                        pedido.put(
                                "pergunta",
                                texto
                        );

                        JSONArray arrayHistorico =
                                new JSONArray();

                        for (
                                JSONObject item :
                                historico
                        ) {

                            arrayHistorico.put(
                                    item
                            );
                        }

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
                                new URL(
                                        API_URL
                                );

                        connection =
                                (HttpURLConnection)
                                        url.openConnection();

                        connection.setRequestMethod(
                                "POST"
                        );

                        connection.setRequestProperty(
                                "Content-Type",
                                "application/json; charset=UTF-8"
                        );

                        connection.setRequestProperty(
                                "Accept",
                                "application/json"
                        );

                        connection.setDoOutput(
                                true
                        );

                        connection.setConnectTimeout(
                                30000
                        );

                        connection.setReadTimeout(
                                60000
                        );

                        byte[] dados =
                                pedido
                                        .toString()
                                        .getBytes(
                                                StandardCharsets.UTF_8
                                        );

                        OutputStream saida =
                                connection
                                        .getOutputStream();

                        saida.write(
                                dados
                        );

                        saida.flush();
                        saida.close();

                        int responseCode =
                                connection
                                        .getResponseCode();

                        InputStream entradaResposta;

                        if (
                                responseCode >= 200
                                        && responseCode < 300
                        ) {

                            entradaResposta =
                                    connection
                                            .getInputStream();

                        } else {

                            entradaResposta =
                                    connection
                                            .getErrorStream();
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

                        String tipo =
                                resposta.optString(
                                        "tipo",
                                        ""
                                );

                        // ====================================================
                        // IMAGEM
                        // ====================================================

                        if (
                                sucesso
                                        && tipo.equalsIgnoreCase(
                                                "imagem"
                                        )
                        ) {

                            String imagem =
                                    resposta.optString(
                                            "imagem",
                                            ""
                                    );

                            runOnUiThread(
                                    () -> {

                                        removerMensagemPensando();

                                        adicionarMensagem(
                                                "Imagem gerada com sucesso."
                                        );

                                        if (
                                                !imagem.isEmpty()
                                        ) {

                                            adicionarImagemNaTela(
                                                    imagem
                                            );
                                        }
                                    }
                            );

                            return;
                        }

                        // ====================================================
                        // RESPOSTA NORMAL
                        // ====================================================

                        String respostaAlex =
                                resposta.optString(
                                        "resposta",
                                        "Não consegui obter uma resposta."
                                );

                        if (
                                sucesso
                        ) {

                            historico.add(
                                    new JSONObject()
                                            .put(
                                                    "role",
                                                    "user"
                                            )
                                            .put(
                                                    "content",
                                                    texto
                                            )
                            );

                            historico.add(
                                    new JSONObject()
                                            .put(
                                                    "role",
                                                    "model"
                                            )
                                            .put(
                                                    "content",
                                                    respostaAlex
                                            )
                            );
                        }

                        runOnUiThread(
                                () -> {

                                    removerMensagemPensando();

                                    adicionarMensagem(
                                            "Alex: "
                                                    + respostaAlex
                                    );
                                }
                        );

                    } catch (
                            Exception erro
                    ) {

                        runOnUiThread(
                                () -> {

                                    removerMensagemPensando();

                                    adicionarMensagem(
                                            "Alex: Não consegui conectar ao servidor agora."
                                    );
                                }
                        );

                    } finally {

                        if (
                                connection != null
                        ) {

                            connection.disconnect();
                        }
                    }
                }
        );
    }

    // ============================================================
    // LER RESPOSTA
    // ============================================================

    private String lerResposta(
            InputStream entrada
    ) throws Exception {

        if (
                entrada == null
        ) {

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
                (
                        linha =
                                leitor.readLine()
                )
                        != null
        ) {

            resultado.append(
                    linha
            );
        }

        leitor.close();

        return resultado.toString();
    }

    // ============================================================
    // CARREGAR IMAGEM
    // ============================================================

    private void adicionarImagemNaTela(
            String imagem
    ) {

        if (
                imagem == null
                        || imagem.trim().isEmpty()
        ) {

            return;
        }

        executor.execute(
                () -> {

                    HttpURLConnection conexaoImagem =
                            null;

                    try {

                        String urlImagem =
                                imagem.trim();

                        if (
                                !urlImagem.startsWith(
                                        "http://"
                                )
                                        &&
                                !urlImagem.startsWith(
                                        "https://"
                                )
                        ) {

                            urlImagem =
                                    "https://ultra-ia-pro.onrender.com"
                                            + (
                                                urlImagem.startsWith(
                                                        "/"
                                                )
                                                        ? urlImagem
                                                        : "/" + urlImagem
                                            );
                        }

                        URL url =
                                new URL(
                                        urlImagem
                                );

                        conexaoImagem =
                                (HttpURLConnection)
                                        url.openConnection();

                        conexaoImagem.setRequestMethod(
                                "GET"
                        );

                        conexaoImagem.setConnectTimeout(
                                30000
                        );

                        conexaoImagem.setReadTimeout(
                                60000
                        );

                        conexaoImagem.connect();

                        int codigo =
                                conexaoImagem
                                        .getResponseCode();

                        if (
                                codigo < 200
                                        || codigo >= 300
                        ) {

                            throw new Exception(
                                    "Servidor de imagem respondeu HTTP "
                                            + codigo
                            );
                        }

                        InputStream entrada =
                                conexaoImagem
                                        .getInputStream();

                        Bitmap bitmap =
                                BitmapFactory
                                        .decodeStream(
                                                entrada
                                        );

                        entrada.close();

                        if (
                                bitmap == null
                        ) {

                            throw new Exception(
                                    "Não foi possível decodificar a imagem."
                            );
                        }

                        runOnUiThread(
                                () -> {

                                    ImageView imagemView =
                                            new ImageView(
                                                    MainActivity.this
                                            );

                                    imagemView.setImageBitmap(
                                            bitmap
                                    );

                                    imagemView.setAdjustViewBounds(
                                            true
                                    );

                                    imagemView.setScaleType(
                                            ImageView.ScaleType
                                                    .FIT_CENTER
                                    );

                                    GradientDrawable fundoImagem =
                                            new GradientDrawable();

                                    fundoImagem.setColor(
                                            Color.argb(
                                                    150,
                                                    10,
                                                    13,
                                                    20
                                            )
                                    );

                                    fundoImagem.setCornerRadius(
                                            dp(20)
                                    );

                                    imagemView.setBackground(
                                            fundoImagem
                                    );

                                    LinearLayout.LayoutParams parametros =
                                            new LinearLayout.LayoutParams(
                                                    ViewGroup.LayoutParams.MATCH_PARENT,
                                                    ViewGroup.LayoutParams.WRAP_CONTENT
                                            );

                                    parametros.setMargins(
                                            dp(15),
                                            dp(8),
                                            dp(15),
                                            dp(15)
                                    );

                                    mensagens.addView(
                                            imagemView,
                                            parametros
                                    );

                                    rolarChatParaBaixo();
                                }
                        );

                    } catch (
                            Exception erro
                    ) {

                        runOnUiThread(
                                () -> {

                                    adicionarMensagem(
                                            "🖼️ Não foi possível carregar a imagem: "
                                                    + erro.getMessage()
                                    );
                                }
                        );

                    } finally {

                        if (
                                conexaoImagem != null
                        ) {

                            conexaoImagem.disconnect();
                        }
                    }
                }
        );
    }

    // ============================================================
    // PROCESSAR PELA PONTE
    // ============================================================

    private void processarPelaPonte(
            String codigo,
            String instrucao
    ) {

        codigo =
                codigo.trim();

        instrucao =
                instrucao.trim();

        if (
                codigo.isEmpty()
        ) {

            adicionarMensagem(
                    "Ponte: cole um código para processar."
            );

            return;
        }

        if (
                instrucao.isEmpty()
        ) {

            adicionarMensagem(
                    "Ponte: informe o que deseja modificar."
            );

            return;
        }

        adicionarMensagem(
                "Você → Ponte: processando..."
        );

        final String codigoFinal =
                codigo;

        final String instrucaoFinal =
                instrucao;

        executor.execute(
                () -> {

                    HttpURLConnection conexao =
                            null;

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
                                new URL(
                                        PONTE_API_URL
                                );

                        conexao =
                                (HttpURLConnection)
                                        url.openConnection();

                        conexao.setRequestMethod(
                                "POST"
                        );

                        conexao.setRequestProperty(
                                "Content-Type",
                                "application/json"
                        );

                        conexao.setRequestProperty(
                                "Accept",
                                "application/json"
                        );

                        conexao.setDoOutput(
                                true
                        );

                        conexao.setConnectTimeout(
                                30000
                        );

                        conexao.setReadTimeout(
                                90000
                        );

                        byte[] dados =
                                pedido
                                        .toString()
                                        .getBytes(
                                                StandardCharsets.UTF_8
                                        );

                        try (
                                OutputStream saida =
                                        conexao.getOutputStream()
                        ) {

                            saida.write(
                                    dados
                            );
                        }

                        int codigoHttp =
                                conexao
                                        .getResponseCode();

                        InputStream entradaResposta;

                        if (
                                codigoHttp >= 200
                                        && codigoHttp < 300
                        ) {

                            entradaResposta =
                                    conexao
                                            .getInputStream();

                        } else {

                            entradaResposta =
                                    conexao
                                            .getErrorStream();
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

                        if (
                                sucesso
                        ) {

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

                            runOnUiThread(
                                    () -> {

                                        adicionarMensagem(
                                                "Ponte: "
                                                        + status
                                                        + "\nArquivo processado: "
                                                        + nomeArquivo
                                        );

                                        if (
                                                !download.isEmpty()
                                        ) {

                                            Button botaoDownload =
                                                    criarBotaoAcao(
                                                            "📥 Baixar arquivo processado"
                                                    );

                                            botaoDownload.setOnClickListener(
                                                    v -> {

                                                        try {

                                                            String urlDownload =
                                                                    download;

                                                            if (
                                                                    !urlDownload
                                                                            .startsWith(
                                                                                    "http://"
                                                                            )
                                                                            &&
                                                                    !urlDownload
                                                                            .startsWith(
                                                                                    "https://"
                                                                            )
                                                            ) {

                                                                urlDownload =
                                                                        "https://ponte-alex-v2.onrender.com"
                                                                                + (
                                                                                    urlDownload
                                                                                            .startsWith(
                                                                                                    "/"
                                                                                            )
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

                                                        } catch (
                                                                Exception erro
                                                        ) {

                                                            adicionarMensagem(
                                                                    "📥 Não foi possível abrir o download: "
                                                                            + erro.getMessage()
                                                            );
                                                        }
                                                    }
                                            );

                                            adicionarBotaoAoChat(
                                                    botaoDownload
                                            );
                                        }
                                    }
                            );

                        } else {

                            String erro =
                                    resposta.optString(
                                            "error",
                                            resposta.optString(
                                                    "resposta",
                                                    "A Ponte não conseguiu processar."
                                            )
                                    );

                            runOnUiThread(
                                    () -> {

                                        adicionarMensagem(
                                                "Ponte: "
                                                        + erro
                                        );
                                    }
                            );
                        }

                    } catch (
                            Exception erro
                    ) {

                        runOnUiThread(
                                () -> {

                                    adicionarMensagem(
                                            "Ponte: não foi possível conectar ao servidor."
                                    );
                                }
                        );

                    } finally {

                        if (
                                conexao != null
                        ) {

                            conexao.disconnect();
                        }
                    }
                }
        );
    }

    // ============================================================
    // REMOVER "PENSANDO..."
    // ============================================================

    private void removerMensagemPensando() {

        int quantidade =
                mensagens.getChildCount();

        if (
                quantidade == 0
        ) {

            return;
        }

        View ultima =
                mensagens.getChildAt(
                        quantidade - 1
                );

        if (
                ultima instanceof LinearLayout
        ) {

            LinearLayout layout =
                    (LinearLayout) ultima;

            if (
                    layout.getChildCount() > 0
            ) {

                View filho =
                        layout.getChildAt(
                                0
                        );

                if (
                        filho instanceof TextView
                ) {

                    TextView texto =
                            (TextView) filho;

                    if (
                            texto.getText()
                                    .toString()
                                    .equals(
                                            "pensando..."
                                    )
                    ) {

                        mensagens.removeView(
                                ultima
                        );
                    }
                }
            }

        } else if (
                ultima instanceof TextView
        ) {

            TextView texto =
                    (TextView) ultima;

            if (
                    texto.getText()
                            .toString()
                            .equals(
                                    "pensando..."
                            )
            ) {

                mensagens.removeView(
                        ultima
                );
            }
        }
    }

    // ============================================================
    // ADICIONAR MENSAGEM
    // ============================================================

    private void adicionarMensagem(
            String texto
    ) {

        if (
                texto == null
                        || texto.trim().isEmpty()
        ) {

            return;
        }

        boolean mensagemUsuario =
                texto.startsWith(
                        "Você:"
                );

        boolean mensagemAlex =
                texto.startsWith(
                        "Alex:"
                );

        // ========================================================
        // CONTAINER DO BALÃO
        // ========================================================

        LinearLayout linha =
                new LinearLayout(this);

        linha.setOrientation(
                LinearLayout.HORIZONTAL
        );

        linha.setGravity(
                mensagemUsuario
                        ? Gravity.END
                        : Gravity.START
        );

        linha.setPadding(
                dp(4),
                dp(4),
                dp(4),
                dp(4)
        );

        // ========================================================
        // BALÃO
        // ========================================================

        TextView mensagem =
                new TextView(this);

        String textoExibido =
                texto;

        if (
                texto.startsWith("Você:")
        ) {

            textoExibido =
                    texto.substring(
                            "Você:".length()
                    ).trim();

        } else if (
                texto.startsWith("Alex:")
        ) {

            textoExibido =
                    texto.substring(
                            "Alex:".length()
                    ).trim();
        }

        mensagem.setText(
                textoExibido
        );

        mensagem.setTextColor(
                Color.WHITE
        );

        mensagem.setTextSize(
                16
        );

        mensagem.setGravity(
                Gravity.START
        );

        mensagem.setPadding(
                dp(17),
                dp(12),
                dp(17),
                dp(12)
        );

        GradientDrawable fundoMensagem =
                new GradientDrawable();

        if (
                mensagemUsuario
        ) {

            fundoMensagem.setColor(
                    Color.argb(
                            175,
                            55,
                            65,
                            82
                    )
            );

        } else {

            fundoMensagem.setColor(
                    Color.argb(
                            150,
                            12,
                            17,
                            27
                    )
            );
        }

        fundoMensagem.setCornerRadius(
                dp(22)
        );

        fundoMensagem.setStroke(
                dp(1),
                Color.argb(
                        55,
                        255,
                        255,
                        255
                )
        );

        mensagem.setBackground(
                fundoMensagem
        );

        // ========================================================
        // LARGURA DO BALÃO
        // ========================================================

        int larguraMaxima =
                (int) (
                        getResources()
                                .getDisplayMetrics()
                                .widthPixels
                                * 0.82f
                );

        LinearLayout.LayoutParams parametrosMensagem =
                new LinearLayout.LayoutParams(
                        larguraMaxima,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                );

        linha.addView(
                mensagem,
                parametrosMensagem
        );

        // ========================================================
        // ADICIONAR AO CHAT
        // ========================================================

        mensagens.addView(
                linha,
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                )
        );

        rolarChatParaBaixo();
    }

    // ============================================================
    // BOTÃO DE AÇÃO NO CHAT
    // ============================================================

    private Button criarBotaoAcao(
            String texto
    ) {

        Button botao =
                new Button(this);

        botao.setText(
                texto
        );

        botao.setTextColor(
                Color.WHITE
        );

        botao.setTextSize(
                14
        );

        GradientDrawable fundo =
                new GradientDrawable();

        fundo.setColor(
                Color.argb(
                        175,
                        20,
                        27,
                        40
                )
        );

        fundo.setCornerRadius(
                dp(18)
        );

        fundo.setStroke(
                dp(1),
                Color.argb(
                        65,
                        255,
                        255,
                        255
                )
        );

        botao.setBackground(
                fundo
        );

        botao.setPadding(
                dp(12),
                dp(5),
                dp(12),
                dp(5)
        );

        return botao;
    }

    // ============================================================
    // ADICIONAR BOTÃO AO CHAT
    // ============================================================

    private void adicionarBotaoAoChat(
            Button botao
    ) {

        LinearLayout.LayoutParams parametros =
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.WRAP_CONTENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT
                );

        parametros.setMargins(
                dp(12),
                dp(5),
                dp(12),
                dp(10)
        );

        mensagens.addView(
                botao,
                parametros
        );

        rolarChatParaBaixo();
    }

    // ============================================================
    // ROLAR CHAT PARA BAIXO
    // ============================================================

    private void rolarChatParaBaixo() {

        if (
                scrollChat == null
        ) {

            return;
        }

        scrollChat.post(
                () -> scrollChat.fullScroll(
                        View.FOCUS_DOWN
                )
        );
    }

    // ============================================================
    // DESTRUIR ACTIVITY
    // ============================================================

    @Override
    protected void onDestroy() {

        executor.shutdownNow();

        super.onDestroy();
    }

    // ============================================================
    // BOTÃO VOLTAR
    // ============================================================

    @Override
    public void onBackPressed() {

        super.onBackPressed();
    }
}

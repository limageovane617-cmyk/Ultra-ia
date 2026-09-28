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

    // ============================================================
    // INTERFACE
    // ============================================================

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

    // ============================================================
    // EXECUTOR
    // ============================================================

    private final ExecutorService executor =
            Executors.newSingleThreadExecutor();

    // ============================================================
    // HISTÓRICO
    // ============================================================

    private final List<JSONObject> historico =
            new ArrayList<>();

    // ============================================================
    // MODO ATUAL
    // ============================================================

    private enum Modo {

        CHAT,

        IMAGEM,

        VIDEO
    }

    private Modo modoAtual =
            Modo.CHAT;

    // ============================================================
    // DURAÇÃO DO VÍDEO
    // ============================================================

    private int duracaoVideo =
            5;

    // ============================================================
    // APIs
    // ============================================================

    private static final String API_BASE_URL =
            "https://ultra-ia-pro.onrender.com";

    private static final String API_URL =
            API_BASE_URL + "/api/chat";

    private static final String IMAGEM_API_URL =
            API_BASE_URL + "/api/imagem";

    private static final String VIDEO_API_URL =
            API_BASE_URL + "/api/video";

    private static final String PONTE_API_URL =
            API_BASE_URL + "/api/ponte/processar";

    // ============================================================
    // CICLO DA ACTIVITY
    // ============================================================

    @Override
    protected void onCreate(
            Bundle savedInstanceState
    ) {

        super.onCreate(
                savedInstanceState
        );

        getWindow().setSoftInputMode(
                WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE
        );

        criarInterface();
    }

    // ============================================================
    // DP
    // ============================================================

    private int dp(
            float valor
    ) {

        return (int) (
                valor
                        * getResources()
                        .getDisplayMetrics()
                        .density
        );
    }

    // ============================================================
    // INTERFACE PRINCIPAL
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
        // FUNDO ULTRA
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
        // CIDADE
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
        // TELA
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
        // CHAT
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

        tela.addView(
                scrollChat,
                new LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        0,
                        1
                )
        );

        // ========================================================
        // ÁREA DE ENTRADA
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
        // CAMPO
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
        // ENTRADA
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
        // FINAL
        // ========================================================

        setContentView(
                raiz
        );
    }

    // ============================================================
    // MENU
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

        popup.showAtLocation(
                raiz,
                Gravity.BOTTOM | Gravity.START,
                dp(16),
                dp(78)
        );
    }

    // ============================================================
    // FERRAMENTAS
    // ============================================================

    private void executarFerramenta(
            String ferramenta
    ) {

        if (
                ferramenta.equals(
                        "🖼️  Imagem"
                )
        ) {

            modoAtual =
                    Modo.IMAGEM;

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
                        "🎬  Vídeo"
                )
        ) {

            modoAtual =
                    Modo.VIDEO;

            campoMensagem.setHint(
                    "Descreva o vídeo que você quer criar..."
            );

            mostrarSelecaoDuracaoVideo();

            campoMensagem.requestFocus();

            adicionarMensagem(
                    "🎬 Modo Vídeo ativado.\n\n"
                            + "Duração selecionada: "
                            + duracaoVideo
                            + " segundos.\n\n"
                            + "Agora descreva o vídeo normalmente."
            );

            return;
        }

        if (
                ferramenta.equals(
                        "🔊  Voz"
                )
        ) {

            adicionarMensagem(
                    "🔊 O modo de voz está disponível "
                            + "quando a função correspondente "
                            + "estiver ligada ao servidor."
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

            historico.clear();

            modoAtual =
                    Modo.CHAT;

            campoMensagem.setHint(
                    "Digite sua mensagem..."
            );

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
    // SELEÇÃO DE DURAÇÃO DO VÍDEO
    // ============================================================

    private void mostrarSelecaoDuracaoVideo() {

        final String[] opcoes = {

                "5 segundos",

                "8 segundos",

                "10 segundos",

                "15 segundos",

                "20 segundos"
        };

        final int[] valores = {

                5,

                8,

                10,

                15,

                20
        };

        int selecionado =
                0;

        for (
                int i = 0;
                i < valores.length;
                i++
        ) {

            if (
                    valores[i]
                            == duracaoVideo
            ) {

                selecionado =
                        i;

                break;
            }
        }

        AlertDialog dialog =
                new AlertDialog.Builder(this)
                        .setTitle(
                                "🎬 Duração do vídeo"
                        )
                        .setSingleChoiceItems(
                                opcoes,
                                selecionado,
                                (d, which) -> {

                                    duracaoVideo =
                                            valores[which];

                                    d.dismiss();

                                    adicionarMensagem(
                                            "🎬 Duração definida para "
                                                    + duracaoVideo
                                                    + " segundos."
                                    );
                                }
                        )
                        .setNegativeButton(
                                "Cancelar",
                                null
                        )
                        .create();

        dialog.show();
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
    // SELETOR DE ARQUIVO
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
    // RESULTADO DO ARQUIVO
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
                        // TEXTO
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
    // LISTAR ZIP
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
    // EXTRAIR APK
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
    // INSTALADOR
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
                                    Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
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
    // NOME ARQUIVO
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
    // LER UTF-8
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

        // ========================================================
        // IMAGEM
        // ========================================================

        if (
                modoAtual
                        == Modo.IMAGEM
        ) {

            modoAtual =
                    Modo.CHAT;

            campoMensagem.setHint(
                    "Digite sua mensagem..."
            );

            gerarImagem(
                    texto
            );

            return;
        }

        // ========================================================
        // VÍDEO
        // ========================================================

        if (
                modoAtual
                        == Modo.VIDEO
        ) {

            modoAtual =
                    Modo.CHAT;

            campoMensagem.setHint(
                    "Digite sua mensagem..."
            );

            gerarVideo(
                    texto,
                    duracaoVideo
            );

            return;
        }

        // ========================================================
        // CHAT NORMAL
        // ========================================================

        adicionarMensagem(
                "Alex: pensando..."
        );

        consultarChat(
                texto
        );
    }

    // ============================================================
    // CHAT GEMINI
    // ============================================================

    private void consultarChat(
            String texto
    ) {

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

                        synchronized (
                                historico
                        ) {

                            for (
                                    JSONObject item :
                                    historico
                            ) {

                                arrayHistorico.put(
                                        item
                                );
                            }
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
                                        connection.getOutputStream()
                        ) {

                            saida.write(
                                    dados
                            );
                        }

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

                        String respostaAlex =
                                resposta.optString(
                                        "resposta",
                                        "Não consegui obter uma resposta."
                                );

                        // ====================================================
                        // IMAGEM GERADA PELO CHAT
                        // ====================================================

                        String imagem =
                                resposta.optString(
                                        "imagem",
                                        ""
                                );

                        if (
                                sucesso
                                        && !imagem.isEmpty()
                        ) {

                            adicionarHistorico(
                                    texto,
                                    respostaAlex
                            );

                            runOnUiThread(
                                    () -> {

                                        removerMensagemPensando();

                                        adicionarMensagem(
                                                "Alex: "
                                                        + respostaAlex
                                        );

                                        adicionarImagemNaTela(
                                                imagem
                                        );
                                    }
                            );

                            return;
                        }

                        // ====================================================
                        // NORMAL
                        // ====================================================

                        if (
                                sucesso
                        ) {

                            adicionarHistorico(
                                    texto,
                                    respostaAlex
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

                                    adicionarMensagem(
                                            "Detalhes: "
                                                    + erro.getMessage()
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
    // HISTÓRICO
    // ============================================================

    private void adicionarHistorico(
            String pergunta,
            String resposta
    ) {

        synchronized (
                historico
        ) {

            try {

                historico.add(
                        new JSONObject()
                                .put(
                                        "role",
                                        "user"
                                )
                                .put(
                                        "content",
                                        pergunta
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
                                        resposta
                                )
                );

                while (
                        historico.size()
                                > 40
                ) {

                    historico.remove(
                            0
                    );
                }

            } catch (
                    Exception ignored
            ) {
            }
        }
    }

    // ============================================================
    // GERAR IMAGEM
    // ============================================================

    private void gerarImagem(
            String prompt
    ) {

        adicionarMensagem(
                "Alex: 🎨 Gerando imagem..."
        );

        executor.execute(
                () -> {

                    HttpURLConnection conexao =
                            null;

                    try {

                        JSONObject pedido =
                                new JSONObject();

                        pedido.put(
                                "prompt",
                                prompt
                        );

                        URL url =
                                new URL(
                                        IMAGEM_API_URL
                                );

                        conexao =
                                (HttpURLConnection)
                                        url.openConnection();

                        conexao.setRequestMethod(
                                "POST"
                        );

                        conexao.setRequestProperty(
                                "Content-Type",
                                "application/json; charset=UTF-8"
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
                                180000
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

                        int codigo =
                                conexao.getResponseCode();

                        InputStream respostaStream;

                        if (
                                codigo >= 200
                                        && codigo < 300
                        ) {

                            respostaStream =
                                    conexao.getInputStream();

                        } else {

                            respostaStream =
                                    conexao.getErrorStream();
                        }

                        String textoResposta =
                                lerResposta(
                                        respostaStream
                                );

                        JSONObject resposta =
                                new JSONObject(
                                        textoResposta
                                );

                        boolean sucesso =
                                resposta.optBoolean(
                                        "success",
                                        false
                                );

                        if (
                                !sucesso
                        ) {

                            String erro =
                                    resposta.optString(
                                            "error",
                                            "Não foi possível gerar a imagem."
                                    );

                            runOnUiThread(
                                    () -> {

                                        adicionarMensagem(
                                                "🖼️ Erro: "
                                                        + erro
                                        );
                                    }
                            );

                            return;
                        }

                        String imagem =
                                resposta.optString(
                                        "imagem",
                                        ""
                                );

                        String motor =
                                resposta.optString(
                                        "motor",
                                        ""
                                );

                        runOnUiThread(
                                () -> {

                                    adicionarMensagem(
                                            "Alex: 🖼️ Imagem gerada com sucesso."
                                                    + (
                                                        motor.isEmpty()
                                                                ? ""
                                                                : "\n🎨 Motor: "
                                                                + motor
                                                    )
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

                    } catch (
                            Exception erro
                    ) {

                        runOnUiThread(
                                () -> {

                                    adicionarMensagem(
                                            "🖼️ Não foi possível gerar a imagem: "
                                                    + erro.getMessage()
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
    // GERAR VÍDEO
    // ============================================================

    private void gerarVideo(
            String prompt,
            int duracao
    ) {

        adicionarMensagem(
                "Alex: 🎬 Gerando vídeo..."
                        + "\n⏱️ Duração: "
                        + duracao
                        + " segundos."
        );

        executor.execute(
                () -> {

                    HttpURLConnection conexao =
                            null;

                    try {

                        JSONObject pedido =
                                new JSONObject();

                        pedido.put(
                                "prompt",
                                prompt
                        );

                        pedido.put(
                                "imagem",
                                JSONObject.NULL
                        );

                        pedido.put(
                                "duracao",
                                duracao
                        );

                        pedido.put(
                                "motor",
                                "automatico"
                        );

                        URL url =
                                new URL(
                                        VIDEO_API_URL
                                );

                        conexao =
                                (HttpURLConnection)
                                        url.openConnection();

                        conexao.setRequestMethod(
                                "POST"
                        );

                        conexao.setRequestProperty(
                                "Content-Type",
                                "application/json; charset=UTF-8"
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
                                300000
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

                        int codigo =
                                conexao.getResponseCode();

                        InputStream respostaStream;

                        if (
                                codigo >= 200
                                        && codigo < 300
                        ) {

                            respostaStream =
                                    conexao.getInputStream();

                        } else {

                            respostaStream =
                                    conexao.getErrorStream();
                        }

                        String textoResposta =
                                lerResposta(
                                        respostaStream
                                );

                        JSONObject resposta =
                                new JSONObject(
                                        textoResposta
                                );

                        boolean sucesso =
                                resposta.optBoolean(
                                        "success",
                                        false
                                );

                        if (
                                !sucesso
                        ) {

                            String erro =
                                    resposta.optString(
                                            "erro",
                                            resposta.optString(
                                                    "error",
                                                    "Não foi possível gerar o vídeo."
                                            )
                                    );

                            runOnUiThread(
                                    () -> {

                                        adicionarMensagem(
                                                "🎬 Erro ao gerar vídeo: "
                                                        + erro
                                        );
                                    }
                            );

                            return;
                        }

                        String video =
                                resposta.optString(
                                        "video",
                                        ""
                                );

                        String motor =
                                resposta.optString(
                                        "motor",
                                        ""
                                );

                        String arquivo =
                                resposta.optString(
                                        "arquivo",
                                        ""
                                );

                        runOnUiThread(
                                () -> {

                                    StringBuilder mensagem =
                                            new StringBuilder();

                                    mensagem.append(
                                            "Alex: 🎬 Vídeo gerado com sucesso."
                                    );

                                    mensagem.append(
                                            "\n⏱️ Duração: "
                                    );

                                    mensagem.append(
                                            duracao
                                    );

                                    mensagem.append(
                                            " segundos."
                                    );

                                    if (
                                            !motor.isEmpty()
                                    ) {

                                        mensagem.append(
                                                "\n🎬 Motor: "
                                        );

                                        mensagem.append(
                                                motor
                                        );
                                    }

                                    if (
                                            !arquivo.isEmpty()
                                    ) {

                                        mensagem.append(
                                                "\n📄 Arquivo: "
                                        );

                                        mensagem.append(
                                                arquivo
                                        );
                                    }

                                    adicionarMensagem(
                                            mensagem.toString()
                                    );

                                    if (
                                            !video.isEmpty()
                                    ) {

                                        adicionarBotaoVideo(
                                                video
                                        );
                                    }
                                }
                        );

                    } catch (
                            Exception erro
                    ) {

                        runOnUiThread(
                                () -> {

                                    adicionarMensagem(
                                            "🎬 Não foi possível gerar o vídeo: "
                                                    + erro.getMessage()
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
    // BOTÃO DO VÍDEO
    // ============================================================

    private void adicionarBotaoVideo(
            String video
    ) {

        String urlVideo =
                normalizarUrl(
                        video
                );

        Button botao =
                criarBotaoAcao(
                        "🎬 Abrir vídeo"
                );

        botao.setOnClickListener(
                v -> {

                    try {

                        Intent navegador =
                                new Intent(
                                        Intent.ACTION_VIEW,
                                        Uri.parse(
                                                urlVideo
                                        )
                                );

                        startActivity(
                                navegador
                        );

                    } catch (
                            Exception erro
                    ) {

                        adicionarMensagem(
                                "🎬 Não foi possível abrir o vídeo: "
                                        + erro.getMessage()
                        );
                    }
                }
        );

        adicionarBotaoAoChat(
                botao
        );
    }

    // ============================================================
    // NORMALIZAR URL
    // ============================================================

    private String normalizarUrl(
            String caminho
    ) {

        if (
                caminho == null
                        || caminho.trim().isEmpty()
        ) {

            return "";
        }

        String valor =
                caminho.trim();

        if (
                valor.startsWith(
                        "http://"
                )
                        ||
                valor.startsWith(
                        "https://"
                )
        ) {

            return valor;
        }

        if (
                !valor.startsWith(
                        "/"
                )
        ) {

            valor =
                    "/" + valor;
        }

        return API_BASE_URL
                + valor;
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
                                normalizarUrl(
                                        imagem
                                );

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
                                120000
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
    // PONTE
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
                                "application/json; charset=UTF-8"
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
                                120000
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
                                                                    normalizarUrl(
                                                                            download
                                                                    );

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
                                                    + "\nDetalhes: "
                                                    + erro.getMessage()
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
    // LER RESPOSTA HTTP
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
    // REMOVER PENSANDO
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
    // MENSAGEM
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

        TextView mensagem =
                new TextView(this);

        String textoExibido =
                texto;

        if (
                texto.startsWith(
                        "Você:"
                )
        ) {

            textoExibido =
                    texto.substring(
                            "Você:".length()
                    ).trim();

        } else if (
                texto.startsWith(
                        "Alex:"
                )
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
    // BOTÃO DE AÇÃO
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
    // ADICIONAR BOTÃO
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
    // ROLAR
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
    // DESTRUIR
    // ============================================================

    @Override
    protected void onDestroy() {

        executor.shutdownNow();

        super.onDestroy();
    }

    // ============================================================
    // VOLTAR
    // ============================================================

    @Override
    public void onBackPressed() {

        super.onBackPressed();
    }
    }

const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');
const { SupabaseUploader } = require('./supabase_uploader');

/**
 * Configurações do scraper
 */
const DEFAULT_OPTIONS = {
  timeout: 60000,        // 60 segundos de timeout
  waitTime: 5000,        // Tempo adicional para aguardar carregamento do JavaScript
  screenshotDir: null,   // Diretório para salvar screenshots (null = desabilitado)
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
  retries: 3,            // Número de tentativas em caso de falha
  retryDelay: 5000,      // Tempo de espera entre as tentativas (5 segundos)
  outputDir: './output', // Diretório de saída
  headless: 'new',       // Modo headless do Puppeteer
  executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || null // Caminho para o Chrome/Chromium
};

/**
 * Classe para realizar o scraping de páginas do Airbnb com Puppeteer
 */
class PuppeteerAirbnbScraper {
  /**
   * Construtor
   * @param {Object} options - Opções de configuração
   */
  constructor(options = {}) {
    this.options = { ...DEFAULT_OPTIONS, ...options };
    this.browser = null;
  }

  /**
   * Inicializa o browser
   */
  async initialize() {
    if (this.browser) {
      return;
    }

    console.log('Inicializando o navegador Puppeteer...');
    try {
      const puppeteerConfig = {
        headless: this.options.headless,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-accelerated-2d-canvas',
          '--disable-gpu',
          '--window-size=1920,1080',
          '--disable-extensions',
          '--disable-features=site-per-process',
          '--disable-web-security'
        ],
        defaultViewport: {
          width: 1920,
          height: 1080
        },
        // No Replit, é melhor ignorar as verificações de execução do navegador
        ignoreHTTPSErrors: true,
        dumpio: true // Ajuda no debug mostrando stdout/stderr do navegador
      };
      
      // Adiciona o caminho executável do Chrome/Chromium se especificado
      if (this.options.executablePath) {
        console.log(`Usando Chrome/Chromium em: ${this.options.executablePath}`);
        puppeteerConfig.executablePath = this.options.executablePath;
      } else {
        // Tenta localizar o Chrome/Chromium no sistema
        try {
          const { execSync } = require('child_process');
          const chromiumPath = execSync('which chromium').toString().trim();
          if (chromiumPath) {
            console.log(`Chromium encontrado em: ${chromiumPath}`);
            puppeteerConfig.executablePath = chromiumPath;
          }
        } catch (e) {
          console.log('Chromium não encontrado no PATH, usando o Chromium integrado do Puppeteer.');
        }
      }
      
      this.browser = await puppeteer.launch(puppeteerConfig);
      console.log('Navegador inicializado com sucesso!');
    } catch (error) {
      console.error('Erro ao inicializar o navegador:', error.message);
      
      // Verificar se o erro está relacionado a bibliotecas ausentes
      if (error.message.includes('shared libraries') || error.message.includes('cannot open shared object file')) {
        console.error('ERRO DE DEPENDÊNCIAS: Algumas bibliotecas necessárias estão faltando no sistema.');
        console.error('Recomendação: Execute o script em ambiente Docker ou instale as dependências necessárias.');
      }
      
      throw error;
    }
  }

  /**
   * Fecha o browser
   */
  async close() {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
      console.log('Navegador fechado.');
    }
  }

  /**
   * Cria um novo nome de arquivo com timestamp
   * @param {string} roomId - ID do quarto do Airbnb
   * @returns {string} Nome do arquivo
   */
  createFilename(roomId) {
    const date = new Date();
    const timestamp = date.toISOString()
      .replace(/:/g, '-')
      .replace(/\..+/, '')
      .replace('T', 'T');
    
    return `airbnb_${roomId}_${timestamp}.html`;
  }

  /**
   * Garante que o diretório de saída existe
   * @param {string} dir - Caminho do diretório
   */
  async ensureDir(dir) {
    try {
      await fs.mkdir(dir, { recursive: true });
    } catch (error) {
      if (error.code !== 'EEXIST') {
        throw error;
      }
    }
  }

  /**
   * Formata a URL do Airbnb
   * @param {string} roomId - ID do quarto
   * @returns {string} URL completa
   */
  formatUrl(roomId) {
    return `https://www.airbnb.com.br/rooms/${roomId}`;
  }

  /**
   * Realiza o scraping de uma página do Airbnb
   * @param {string} roomId - ID do quarto
   * @returns {Promise<string>} Caminho do arquivo HTML salvo
   */
  async scrapeRoom(roomId) {
    if (!/^\d+$/.test(roomId)) {
      throw new Error(`ID do quarto inválido: ${roomId}. Deve conter apenas números.`);
    }

    await this.ensureDir(this.options.outputDir);
    await this.initialize();

    const url = this.formatUrl(roomId);
    console.log(`Iniciando scraping da página: ${url}`);

    let attempt = 0;
    let lastError = null;

    while (attempt < this.options.retries) {
      attempt++;
      console.log(`Tentativa ${attempt} de ${this.options.retries}...`);

      try {
        // Abre uma nova página
        const page = await this.browser.newPage();

        // Configura o User-Agent
        await page.setUserAgent(this.options.userAgent);

        // Configura o timeout de navegação
        page.setDefaultNavigationTimeout(this.options.timeout);

        // Removemos a interceptação de requisições para permitir todas as cargas de recursos
        // Isso pode ajudar a evitar detecção como bot
        await page.setRequestInterception(false);

        // Navega para a URL
        console.log(`Navegando para: ${url}`);
        await page.goto(url, { 
          waitUntil: 'networkidle2',
          timeout: this.options.timeout
        });

        // Espera adicional para garantir que todo o conteúdo esteja carregado
        console.log(`Aguardando ${this.options.waitTime}ms para garantir carregamento completo...`);
        // Em versões mais antigas do Puppeteer, pode ser necessário usar page.waitFor() em vez de page.waitForTimeout()
        try {
          if (typeof page.waitForTimeout === 'function') {
            await page.waitForTimeout(this.options.waitTime);
          } else if (typeof page.waitFor === 'function') {
            await page.waitFor(this.options.waitTime);
          } else {
            // Fallback usando setTimeout se os métodos acima não estiverem disponíveis
            await new Promise(resolve => setTimeout(resolve, this.options.waitTime));
          }
        } catch (e) {
          console.log('Erro ao usar waitForTimeout, usando setTimeout como fallback:', e.message);
          await new Promise(resolve => setTimeout(resolve, this.options.waitTime));
        }

        // Verificar se há mensagem de erro de JavaScript
        const javaScriptErrorExists = await page.evaluate(() => {
          const errorMsg = document.body.innerText.includes('algumas partes do site do Airbnb não funcionam corretamente sem a habilitação do JavaScript');
          return errorMsg;
        });

        if (javaScriptErrorExists) {
          console.log('Detectada mensagem de erro de JavaScript. Tentando superar as proteções anti-bot...');
          
          // Scroll para simular interação humana
          await page.evaluate(() => {
            window.scrollBy(0, 500);
          });
          
          await page.waitForTimeout(2000);
          
          // Clique em algum elemento da página para simular interação
          try {
            await page.click('body');
          } catch (e) {
            console.log('Não foi possível clicar no corpo da página');
          }
          
          await page.waitForTimeout(2000);
          
          // Recarregar a página
          await page.reload({ waitUntil: 'networkidle2' });
          
          // Espera adicional após o reload
          await page.waitForTimeout(10000);
        }
        
        // Verifica se o elemento específico foi carregado
        const elementExists = await page.evaluate(() => {
          const elements = document.querySelectorAll('h2.atm_7l_1kw7nm4');
          return elements.length > 0;
        });

        if (!elementExists) {
          console.log('Aviso: O elemento h2 específico não foi encontrado na página.');
          console.log('Verificando conteúdo da página para confirmar carregamento...');
          
          // Verificação adicional para garantir que a página carregou completamente
          const pageTitle = await page.title();
          console.log(`Título da página: ${pageTitle}`);
          
          if (!pageTitle.includes('Airbnb')) {
            throw new Error('A página não carregou corretamente (título não contém "Airbnb")');
          }
        } else {
          console.log('Elemento h2 específico encontrado na página!');
        }

        // Obtém o HTML completo da página
        console.log('Extraindo conteúdo HTML completo...');
        const content = await page.content();
        
        if (content.length < 5000) {
          throw new Error(`Conteúdo HTML muito pequeno (${content.length} bytes), possivelmente incompleto`);
        }
        
        // Extrair o título da página para atualizar no Supabase
        const title = await page.evaluate(() => {
          // Tentar diferentes seletores para título
          const selectors = [
            'h1[data-testid="listing-title"]',
            'h1._fecoyn4',
            'h1.atm_7l_1kw7nm4',
            'h2.atm_7l_1kw7nm4',
            'h1'  // Fallback genérico
          ];
          
          for (const selector of selectors) {
            const elem = document.querySelector(selector);
            if (elem) {
              return elem.innerText.trim();
            }
          }
          
          // Se tudo falhar, usar o título da página
          const pageTitle = document.title;
          if (pageTitle && pageTitle.includes(' - Airbnb')) {
            return pageTitle.split(' - Airbnb')[0].trim();
          }
          
          return pageTitle || null;
        });
        
        if (title) {
          console.log(`Título extraído: "${title}"`);
        } else {
          console.log('Não foi possível extrair o título da página');
        }

        // Captura screenshot (opcional)
        if (this.options.screenshotDir) {
          await this.ensureDir(this.options.screenshotDir);
          const screenshotPath = path.join(
            this.options.screenshotDir,
            `airbnb_${roomId}_${new Date().toISOString().replace(/:/g, '-')}.png`
          );
          console.log(`Capturando screenshot para: ${screenshotPath}`);
          await page.screenshot({ path: screenshotPath, fullPage: true });
        }

        // Salva o conteúdo HTML
        const filename = this.createFilename(roomId);
        const outputPath = path.join(this.options.outputDir, filename);
        console.log(`Salvando HTML em: ${outputPath}`);
        await fs.writeFile(outputPath, content);

        // Exibe o tamanho do arquivo
        const stats = await fs.stat(outputPath);
        const fileSizeKB = (stats.size / 1024).toFixed(2);
        console.log(`Tamanho do arquivo: ${fileSizeKB} KB`);

        // Fecha a página
        await page.close();

        // Retorna o caminho do arquivo e o título
        return { outputPath, title };
      } catch (error) {
        lastError = error;
        console.error(`Erro na tentativa ${attempt}:`, error.message);
        
        if (attempt < this.options.retries) {
          console.log(`Aguardando ${this.options.retryDelay}ms antes da próxima tentativa...`);
          await new Promise(resolve => setTimeout(resolve, this.options.retryDelay));
        }
      }
    }

    throw new Error(`Falha após ${this.options.retries} tentativas. Último erro: ${lastError.message}`);
  }
}

/**
 * Função principal
 */
async function main() {
  // Processa argumentos da linha de comando
  const args = process.argv.slice(2);
  let roomId = null;
  let outputDir = DEFAULT_OPTIONS.outputDir;
  let screenshotDir = null;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--room-id' && i + 1 < args.length) {
      roomId = args[i + 1];
      i++;
    } else if (args[i] === '--output-dir' && i + 1 < args.length) {
      outputDir = args[i + 1];
      i++;
    } else if (args[i] === '--screenshot-dir' && i + 1 < args.length) {
      screenshotDir = args[i + 1];
      i++;
    } else if (args[i].startsWith('--room-id=')) {
      roomId = args[i].substring('--room-id='.length);
    } else if (args[i].startsWith('--output-dir=')) {
      outputDir = args[i].substring('--output-dir='.length);
    } else if (args[i].startsWith('--screenshot-dir=')) {
      screenshotDir = args[i].substring('--screenshot-dir='.length);
    } else if (!roomId) {
      // Assume que o primeiro argumento desconhecido é o room_id
      roomId = args[i];
    }
  }

  if (!roomId) {
    console.error('Error: ID do quarto (room_id) é obrigatório');
    console.log('Uso: node puppeteer_scraper.js --room-id=ROOM_ID [--output-dir=./output] [--screenshot-dir=./screenshots]');
    console.log('ou: node puppeteer_scraper.js ROOM_ID [OUTPUT_DIR]');
    process.exit(1);
  }

  const scraper = new PuppeteerAirbnbScraper({
    outputDir,
    screenshotDir,
    waitTime: 15000, // Aumentando o tempo de espera para 15 segundos
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36', // User agent atualizado
  });

  try {
    console.log(`Iniciando scraping para o quarto ID: ${roomId}`);
    console.log(`Diretório de saída: ${outputDir}`);
    
    // Executar o scraping
    const { outputPath, title } = await scraper.scrapeRoom(roomId);
    console.log(`Scraping concluído com sucesso! Arquivo salvo em: ${outputPath}`);
    
    // Atualizar o título no Supabase se temos ambos roomId e título
    if (roomId && title) {
      try {
        // Verificar se temos as variáveis de ambiente necessárias para o Supabase
        if (process.env.SUPABASE_URL && process.env.SUPABASE_KEY) {
          console.log('Iniciando atualização no Supabase...');
          
          const supabaseUploader = new SupabaseUploader();
          const result = await supabaseUploader.updateRoomLabel(roomId, title);
          
          if (result.success) {
            console.log(`✅ Supabase atualizado com sucesso para o quarto ${roomId}`);
          } else {
            console.error(`❌ Falha ao atualizar o Supabase:`, result.error);
          }
        } else {
          console.log('Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não configuradas. Pulando atualização do Supabase.');
        }
      } catch (supabaseError) {
        console.error('Erro ao atualizar o Supabase:', supabaseError.message);
      }
    } else {
      console.log('Título não extraído. Não é possível atualizar o Supabase.');
    }
  } catch (error) {
    console.error('Erro durante o scraping:', error.message);
    process.exit(1);
  } finally {
    await scraper.close();
  }
}

// Executa a função principal se este arquivo for executado diretamente
if (require.main === module) {
  main();
}

module.exports = {
  PuppeteerAirbnbScraper
};
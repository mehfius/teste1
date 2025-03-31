import { retry } from "./deps.ts";
import { formatUrl } from "./utils.ts";

interface ScraperOptions {
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  userAgent?: string;
}

/**
 * Scrapes the HTML content from an Airbnb listing using fetch
 */
export class AirbnbScraper {
  private readonly timeout: number;
  private readonly retries: number;
  private readonly retryDelay: number;
  private readonly userAgent: string;

  /**
   * Creates a new AirbnbScraper instance
   * @param options Configuration options for the scraper
   */
  constructor(options: ScraperOptions = {}) {
    this.timeout = options.timeout || 30000; // 30 seconds default timeout
    this.retries = options.retries || 3;
    this.retryDelay = options.retryDelay || 2000; // 2 seconds between retries
    this.userAgent = options.userAgent || 
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36';
  }

  /**
   * Scrapes the HTML content for a specific Airbnb room
   * @param roomId The Airbnb room ID to scrape
   * @returns The full HTML content of the page
   */
  async scrapeRoom(roomId: string): Promise<string> {
    console.log(`Starting to scrape room ID: ${roomId}`);
    
    // Create the URL for the room
    const url = formatUrl(roomId);
    console.log(`Fetching URL: ${url}`);
    
    try {
      // Use retry to handle potential network issues
      return await retry(
        async (): Promise<string> => {
          console.log(`Sending HTTP request to ${url}...`);
          
          const controller = new AbortController();
          const timeoutId = setTimeout(() => {
            controller.abort();
          }, this.timeout);
          
          try {
            const response = await fetch(url, {
              signal: controller.signal,
              headers: {
                'User-Agent': this.userAgent,
                'Accept': 'text/html,application/xhtml+xml,application/xml',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
              }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
              throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            console.log(`Response received with status: ${response.status}`);
            const htmlContent = await response.text();
            console.log(`HTML content fetched (length: ${htmlContent.length} characters)`);
            
            return htmlContent;
          } catch (error) {
            clearTimeout(timeoutId);
            console.error(`Error fetching URL: ${error.message}`);
            throw error;
          }
        },
        {
          maxAttempts: this.retries,
          delay: this.retryDelay,
          onError: (error: Error, attempt: number) => {
            console.error(`Attempt ${attempt} failed: ${error.message}`);
            if (attempt < this.retries) {
              console.log(`Retrying in ${this.retryDelay / 1000} seconds...`);
            }
          },
        }
      );
    } catch (error) {
      throw new Error(`Failed to scrape room after ${this.retries} attempts: ${error.message}`);
    }
  }
}

import os
import pandas as pd
import matplotlib.pyplot as plt
import squarify
from telegram import Update
import numpy as np
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Constants for conversation states
SELECTING_ANALYSIS, SELECTING_COIN, SELECTING_VISUALIZATION_GENERAL, SELECTING_VISUALIZATION_SPECIFIC = range(4)

# Load cryptocurrency data
data = pd.read_excel(r"C:\Users\SAIF ASHFEE\OneDrive\Desktop\Data Analysis\Projects\Web Scraper to Telegram Bot\resampled_data.xlsx")

coin_names = pd.read_csv(r"C:\Users\SAIF ASHFEE\OneDrive\Desktop\Data Analysis\Projects\Web Scraper to Telegram Bot\Coin Name.csv")

# Ensure the output directory exists
output_dir = "C:/Temp/generated_images"
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the bot and ask for general or specific coin analysis."""
    await update.message.reply_text(
        "Welcome! Would you like to perform:\n"
        "1. General analysis\n"
        "2. Specific coin analysis\n"
        "Reply with 1 or 2."
    )
    return SELECTING_ANALYSIS


async def select_analysis_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Choose whether the user wants general or specific coin analysis."""
    choice = int(update.message.text.strip())

    if choice == 1:
        # General Analysis
        await update.message.reply_text(
            "Please choose a general visualization option:\n"
            "1. Price Trend\n"
            "2. Market Cap Comparison\n"
            "3. Volume Distribution\n"
            "4. Risk Volatility Analysis\n"
            "5. Top Gainers/Losers\n"
            "6. Trading Activity\n"
            "7. Market Cap Share\n"
            "Reply with the option number."
        )
        return SELECTING_VISUALIZATION_GENERAL


    elif choice == 2:
        # Specific Coin Analysis
        all_coins = coin_names['Coin Name'].unique()
        coin_list = "\n".join(all_coins)
        
        await update.message.reply_text(
            f"Here are the available coins:\n{coin_list}\n\n"
            "Please type the name of the coin you want to fetch the details of: "
        )
        return SELECTING_COIN

    else:
        await update.message.reply_text("Invalid choice. Please reply with 1 or 2.")
        return SELECTING_ANALYSIS


async def select_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store the selected coin for specific analysis."""
    coin_name = update.message.text.strip()
    context.user_data['chosen_coin'] = coin_name

    # Show visualization options for specific coin
    await update.message.reply_text(
        "Please choose a visualization option for the specific coin:\n"
        "1. Market Cap Rank\n"
        "2. Price\n"
        "3. Trading Volume\n"
        "4. Price Change Percentage\n"
        "5. Market Cap\n"
        "6. Last Updated Time\n"
        "Reply with the option number."
    )
    return SELECTING_VISUALIZATION_SPECIFIC


async def select_visualization_general(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle general visualization requests."""
    choice = int(update.message.text.strip())
    all_coins = True  # General analysis always applies to all coins

    try:
        if choice == 1:
            # Price Trend (Line chart for all coins, limited to top 10)
            plt.figure(figsize=(12, 6))
            top_coins = data.groupby('Coin Name').agg({'Last Traded Price($)': 'mean'}).sort_values(
                'Last Traded Price($)', ascending=False).head(10)
            for coin in top_coins.index:
                coin_data = data[data['Coin Name'] == coin]
                plt.plot(coin_data['Last Updated'],
                         coin_data['Last Traded Price($)'], label=coin)
            plt.title("Price Trends for Top 10 Coins")
            plt.xlabel("Date")
            plt.ylabel("Price ($)")
            plt.legend()
            filename = os.path.join(output_dir, "top_10_coins_price_trend.png")

        elif choice == 2:
            # Market Cap Comparison (Horizontal bar chart)
            plt.figure(figsize=(12, 6))
            top_coins = data.groupby('Coin Name').agg({'Market Cap ($)': 'max'}).sort_values(
                'Market Cap ($)', ascending=False).head(10)
            # Generate distinct colors
            colors = plt.cm.Paired(range(len(top_coins)))
            plt.barh(top_coins.index,
                     top_coins['Market Cap ($)'], color=colors)
            plt.title("Market Cap Comparison for Top 10 Coins")
            plt.xlabel("Market Cap ($)")
            plt.ylabel("Coin Name")
            plt.gca().invert_yaxis()  # Flip the order to show the largest on top
            filename = os.path.join(
                output_dir, "top_10_market_cap_comparison.png")

        elif choice == 3:
            # Volume Distribution (Stacked Bar Chart)
            top_coins = data.groupby('Coin Name').agg({'Total Volume': 'sum', 'Circulating Supply': 'mean'}).sort_values(
                'Total Volume', ascending=False).head(10)
            categories = ['Total Volume', 'Circulating Supply']
            values = [top_coins[category] for category in categories]

            plt.figure(figsize=(12, 6))
            for i, category in enumerate(categories):
                plt.bar(top_coins.index, top_coins[category], bottom=np.sum(
                    values[:i], axis=0) if i > 0 else None, label=category)

            plt.title("Stacked Volume Distribution for Top 10 Coins")
            plt.xlabel("Coin Name")
            plt.ylabel("Volume")
            plt.xticks(rotation=45)
            plt.legend(title="Categories")
            filename = os.path.join(
                output_dir, "volume_distribution_stacked_bar.png")
            plt.savefig(filename, bbox_inches='tight')
            print(f"Saved chart to {filename}")


        elif choice == 4:
            # Risk Volatility Analysis (Refined Bubble Chart)
            plt.figure(figsize=(12, 7))
    
            # Calculate volatility and prepare the top coins data
            data['Volatility'] = data['24h High ($)'] - data['24h Low ($)']
            top_coins = data.groupby('Coin Name').agg({
                'Volatility': 'max',
                'Market Cap ($)': 'max',
                'Total Volume': 'sum'
            }).sort_values('Volatility', ascending=False).head(10)

            # Scale bubble sizes (smaller)
            sizes = top_coins['Total Volume'] / 1e7  # Decreased scaling factor

            # Create scatter plot
            scatter = plt.scatter(
                top_coins['Market Cap ($)'],
                top_coins['Volatility'],
                s=sizes,
                alpha=0.6,
                c=top_coins['Volatility'],
                cmap='plasma'
            )
    
            # Add a color bar for context
            plt.colorbar(scatter, label="Volatility ($)")
            plt.title("Risk Volatility vs Market Cap (Bubble Chart)")
            plt.xlabel("Market Cap ($)")
            plt.ylabel("Volatility ($)")

            # Annotate top 5 coins
            for i, (coin, row) in enumerate(top_coins.iterrows()):
                if i < 5:  # Annotate top 5 volatile coins
                    plt.annotate(
                    coin,
                    (row['Market Cap ($)'], row['Volatility']),
                    fontsize=10,
                    ha='right',
                    bbox=dict(boxstyle="round,pad=0.3", edgecolor="gray", facecolor="white", alpha=0.8)
                )

             # Save the chart
            filename = os.path.join(output_dir, "risk_volatility_bubble_chart_refined.png")
            plt.savefig(filename, bbox_inches='tight')
            print(f"Saved chart to {filename}")
                                                                                                                                                        

        elif choice == 5:
                
            # Assuming `df` is your DataFrame
            # Example columns: ['ID', 'Coin Name', 'Last Updated', 'Last Traded Price($)', ...]

            # Step 1: Ensure 'Last Traded Price($)' is numeric
            data['Last Traded Price($)'] = pd.to_numeric(data['Last Traded Price($)'], errors='coerce')

            # Step 2: Get the earliest and latest prices for each coin
            agg_data = data.groupby('Coin Name').agg(
                first_price=('Last Traded Price($)', 'first'),
                last_price=('Last Traded Price($)', 'last')
                ).reset_index()

            # Step 3: Calculate the percentage change
            agg_data['Price Change Percentage'] = ((agg_data['last_price'] - agg_data['first_price']) / agg_data['first_price']) * 100

            # Step 4: Get top gainers and losers
            top_gainers = agg_data.nlargest(5, 'Price Change Percentage')
            top_losers = agg_data.nsmallest(5, 'Price Change Percentage').sort_values(by='Price Change Percentage', ascending=False)

            # Step 5: Combine gainers and losers
            top_gainers['Color'] = 'green'
            top_losers['Color'] = 'red'
            top_combined = pd.concat([top_gainers, top_losers])

            # Step 6: Plot the results
            plt.figure(figsize=(12, 6))
            bars = plt.bar(
                top_combined['Coin Name'], 
                top_combined['Price Change Percentage'], 
                color=top_combined['Color']
            )

            # Add a zero line
            plt.axhline(0, color='black', linewidth=1)

            # Labeling
            plt.xlabel('Coins')
            plt.ylabel('Percentage Change')
            plt.title('Top 5 Gainers and Losers')
            plt.xticks(rotation=45)
            plt.tight_layout()
                
            # Save the chart
            filename = os.path.join(output_dir, "top_gainers_losers_chart.png")
            # plt.savefig(filename, bbox_inches='tight')
            print(f"Saved chart to {filename}")


        elif choice == 6:
            # Step 1: Group by Coin Name and sum the Total Volume
            grouped_df = data.groupby('Coin Name')['Total Volume'].sum().reset_index()
            # Step 2: Sort by total trading volume and select the top 10 unique coins
            top_10_coins = grouped_df.nlargest(10, 'Total Volume')
            
            # Step 3: Calculate percentage share of total volume
            total_volume = top_10_coins['Total Volume'].sum()
            top_10_coins['Percentage'] = (top_10_coins['Total Volume'] / total_volume) * 100
            # Step 4: Create a pie chart
            plt.figure(figsize=(10, 8))
            colors = plt.cm.tab10(range(len(top_10_coins)))  # Generate distinct colors
            plt.title('Share of top 10 coins by trading activity')
            # Plotting
            patches, texts, autotexts = plt.pie(
                top_10_coins['Total Volume'],
                labels=top_10_coins['Coin Name'],
                autopct=lambda p: f'{p:.1f}%' if p > 5 else '',
                colors=colors,
                startangle=140,
                textprops={'fontsize': 10}
                )
            # Adjust label placement for readability
            for text in texts:
                text.set_fontsize(10)
                
            filename = os.path.join(output_dir, "top_gainers_losers_chart.png")
            # plt.savefig(filename, bbox_inches='tight')
            print(f"Saved chart to {filename}")



        elif choice == 7:
            # Market Cap Share (Treemap)

            # Group by Coin Name and sum the Market Cap
            grouped_data = data.groupby('Coin Name', as_index=False).agg({'Market Cap ($)': 'sum'})

            # Sort by Market Cap and exclude Bitcoin
            top_coins = grouped_data.sort_values(by='Market Cap ($)', ascending=False).head(10)
            # Extract data for plotting
            sizes = top_coins['Market Cap ($)']  # Sizes of the blocks
            labels = [f"{coin}\n${cap:.2e}" for coin, cap in zip(top_coins['Coin Name'], sizes)]  # Labels for each block
            # colors = plt.cm.viridis(sizes / sizes.max())  # Normalize sizes for colors
            colors = plt.cm.tab10(range(len(sizes)))

            # Plot the Treemap
            plt.figure(figsize=(15, 10))
            squarify.plot(sizes=sizes, label=labels, color=colors, alpha=0.8)
            plt.title("Treemap of Market Cap Share", fontsize=32)
            plt.axis('off')  # Turn off axis
            filename = os.path.join(output_dir, "top_market_cap_share.png")

        else:
            await update.message.reply_text("Invalid choice. Please choose a valid option.")
            return SELECTING_VISUALIZATION_GENERAL

        # Save the figure and send
        try:
            plt.savefig(filename)
            print(f"Plot successfully saved to {filename}")  # Debugging
            plt.close()  # Close after saving
        except Exception as e:
            print(f"Error saving plot: {e}")

        # Send the generated image
        with open(filename, "rb") as image_file:
            await update.message.reply_photo(photo=image_file)

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

    return ConversationHandler.END


async def select_visualization_specific(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle specific coin visualization requests."""
    choice = int(update.message.text.strip())
    coin_name = context.user_data['chosen_coin']

    try:
        if choice == 1:
            # Market Cap Rank
            max_market_cap = data.groupby('Coin Name')['Market Cap ($)'].max().reset_index()

            # Rank coins based on maximum Market Cap ($)
            max_market_cap['Market Cap Rank'] = max_market_cap['Market Cap ($)'].rank(ascending=False, method='min').astype(int)

            # Find the rank for the chosen coin
            coin_rank_data = max_market_cap[max_market_cap['Coin Name'] == coin_name]
            if coin_rank_data.empty:
                await update.message.reply_text(f"{coin_name} Market Cap data not found.")
                return

            market_cap_rank = coin_rank_data['Market Cap Rank'].iloc[0]
            await update.message.reply_text(f"{coin_name} Market Cap Rank: {market_cap_rank}")
            

        elif choice == 2:
            # Price
            coin_data = data[data['Coin Name'] == coin_name]
            price = coin_data['Last Traded Price($)'].iloc[-1]
            await update.message.reply_text(f"{coin_name} Price: ${price}")

        elif choice == 3:
            # Trading Volume
            coin_data = data[data['Coin Name'] == coin_name]
            volume = coin_data['Total Volume'].iloc[-1]
            await update.message.reply_text(f"{coin_name} Trading Volume: {volume}")

        elif choice == 4:
            # Price Change Percentage
            coin_data = data[data['Coin Name'] == coin_name]
            price_change = coin_data['Price Change Percentage'].iloc[-1]
            await update.message.reply_text(f"{coin_name} Price Change: {price_change}%")

        elif choice == 5:
            # Market Cap
            coin_data = data[data['Coin Name'] == coin_name]
            market_cap = coin_data['Market Cap ($)'].iloc[-1]
            await update.message.reply_text(f"{coin_name} Market Cap: ${market_cap}")

        elif choice == 6:
            # Last Updated Time
            coin_data = data[data['Coin Name'] == coin_name]
            last_updated = coin_data['Last Updated'].iloc[-1]
            await update.message.reply_text(f"{coin_name} Last Updated Time: {last_updated}")

        else:
            await update.message.reply_text("Invalid choice. Please choose a valid option.")

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

    return ConversationHandler.END


def main():
    """Run the bot."""
    application = Application.builder().token(
        "7954453720:AAELjYTyp2lQZ5c5OsNBb3VefuwVoLZhbyc").build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_ANALYSIS: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_analysis_type)],
            SELECTING_COIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_coin)],
            SELECTING_VISUALIZATION_GENERAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_visualization_general)],
            SELECTING_VISUALIZATION_SPECIFIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_visualization_specific)],
        },
        fallbacks=[],
    )

    application.add_handler(conversation_handler)
    application.run_polling()


if __name__ == "__main__":
    main()

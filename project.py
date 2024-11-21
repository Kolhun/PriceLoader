import os
import pandas as pd
from prettytable import PrettyTable

class PriceAnalyzer:
    def __init__(self, folder):
        self.folder = folder
        self.data = pd.DataFrame()

    def load_prices(self):
        files = [f for f in os.listdir(self.folder) if "price" in f.lower()]
        dataframes = []
        for file in files:
            try:
                filepath = os.path.join(self.folder, file)
                df = pd.read_csv(filepath, delimiter=',')

                columns_mapping = {
                    "название": "name", "продукт": "name", "товар": "name", "наименование": "name",
                    "цена": "price", "розница": "price",
                    "фасовка": "weight", "масса": "weight", "вес": "weight"
                }
                df.rename(columns=columns_mapping, inplace=True)
                df = df[["name", "price", "weight"]].copy()
                df["file"] = file
                dataframes.append(df)
            except Exception as e:
                print(f"Ошибка обработки файла {file}: {e}")
        self.data = pd.concat(dataframes, ignore_index=True)
        self.data["price"] = pd.to_numeric(self.data["price"], errors="coerce")
        self.data["weight"] = pd.to_numeric(self.data["weight"], errors="coerce")
        self.data.dropna(subset=["name", "price", "weight"], inplace=True)
        self.data["price_per_kg"] = self.data["price"] / self.data["weight"]

    def export_to_html(self, results=None, output_file: str = "output.html"):
        if results is None:
            results = self.data
        if results.empty:
            print("Нет данных для экспорта.")
            return

        result = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        """
        for index, row in results.iterrows():
            result += f"""
                <tr>
                    <td>{index + 1}</td>
                    <td>{row['name']}</td>
                    <td>{row['price']}</td>
                    <td>{row['weight']}</td>
                    <td>{row['file']}</td>
                    <td>{row['price_per_kg']:.2f}</td>
                </tr>
                """

        result += """
            </table>
        </body>
        </html>
        """

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(result)

        print(f"Данные успешно экспортированы в {output_file}")

    def find_text(self, text):
        if self.data.empty:
            print("Данные не загружены.")
            return []
        result = self.data[self.data["name"].str.contains(text, case=False, na=False)].copy()
        result.sort_values(by="price_per_kg", inplace=True)
        return result

def main():
    analyzer = PriceAnalyzer(folder="files")
    analyzer.load_prices()


    while True:
        query = input("Введите текст для поиска (или 'exit' для выхода): ")
        if query.lower() == "exit":
            print("Работа завершена.")
            break

        results = analyzer.find_text(query)
        if results.empty:
            print("Ничего не найдено.")
            continue

        table = PrettyTable()
        table.field_names = ["№", "Наименование", "Цена", "Вес", "Файл", "Цена за кг"]
        for i, row in results.iterrows():
            table.add_row([i + 1, row["name"], row["price"], row["weight"], row["file"], f"{row['price_per_kg']:.2f}"])
        print(table)
        analyzer.export_to_html(results, "prices.html")


if __name__ == "__main__":
    main()

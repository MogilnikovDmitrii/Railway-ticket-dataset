set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

while true; do
    echo "Настройки платежных систем и банков:"
    echo "1. Оставить стандартные настройки"
    echo "2. Изменить проценты"
    read -r -p "Выберите вариант [1-2]: " settings_choice

    case "$settings_choice" in
        1)
            break
            ;;
        2)
            python -m src.config.configure_payments
            break
            ;;
        *)
            echo "Введите 1 или 2."
            ;;
    esac
done

python -m src.names_generator.names
python -m src.passport_generator.passport
python -m src.groups_generator.groups

python -m src.railway_generator.way

python -m src.railway_generator.train

python -m src.railway_generator.flight

python -m src.railway_generator.carriage

python -m src.railway_generator.seat

python -m src.railway_generator.price

python -m src.railway_generator.assign_tickets

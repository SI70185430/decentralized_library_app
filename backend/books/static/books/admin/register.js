(() => {
  const REGISTER_FORM_ID = "book-register-form";
  const LOOKUP_BUTTON_ID = "btn_book_info";
  const LOOKUP_MESSAGE_ID = "book_lookup_message";
  const CALENDAR_BUTTON_ID = "btn_calendar";
  const ISBN_INPUT_ID = "input_isbn";
  const TITLE_INPUT_ID = "input_title";
  const AUTHOR_INPUT_ID = "input_author";
  const PUBLISHER_INPUT_ID = "input_publisher";
  const PUBLISHED_DATE_INPUT_ID = "input_publication_date";
  const COVER_IMAGE_URL_INPUT_ID = "input_image_url";
  const PRICE_INPUT_ID = "input_price";
  const GENRE_CODE_INPUT_ID = "input_ccode";
  const PURCHASE_DATE_FIELD_SELECTOR = "[data-date-placeholder-field]";
  const DATE_INPUT_SELECTOR = "input[type='date']";
  const ERROR_CLASS_NAME = "book-register-error";
  const HAS_VALUE_CLASS_NAME = "has-value";
  const ISBN_QUERY_PARAM = "isbn";
  const ISBN_REQUIRED_MESSAGE = "ISBNコードを入力してください";
  const LOOKUP_LOADING_MESSAGE = "書籍情報を取得しています...";
  const LOOKUP_FAILED_MESSAGE = "書籍情報を取得できませんでした";
  const LOOKUP_SUCCESS_MESSAGE = "書籍情報を反映しました";

  const registerForm = document.getElementById(REGISTER_FORM_ID);
  const lookupButton = document.getElementById(LOOKUP_BUTTON_ID);
  const message = document.getElementById(LOOKUP_MESSAGE_ID);

  const fields = {
    isbn: document.getElementById(ISBN_INPUT_ID),
    title: document.getElementById(TITLE_INPUT_ID),
    author: document.getElementById(AUTHOR_INPUT_ID),
    publisher: document.getElementById(PUBLISHER_INPUT_ID),
    published_date: document.getElementById(PUBLISHED_DATE_INPUT_ID),
    cover_image_url: document.getElementById(COVER_IMAGE_URL_INPUT_ID),
    price: document.getElementById(PRICE_INPUT_ID),
    genre_code: document.getElementById(GENRE_CODE_INPUT_ID),
  };

  const purchaseDateControl = document.querySelector(PURCHASE_DATE_FIELD_SELECTOR);
  if (purchaseDateControl) {
    const purchaseDateInput = purchaseDateControl.querySelector(DATE_INPUT_SELECTOR);
    const calendarButton = document.getElementById(CALENDAR_BUTTON_ID);
    const syncPurchaseDatePlaceholder = () => {
      purchaseDateControl.classList.toggle(HAS_VALUE_CLASS_NAME, Boolean(purchaseDateInput.value));
    };

    syncPurchaseDatePlaceholder();
    purchaseDateInput.addEventListener("input", syncPurchaseDatePlaceholder);
    purchaseDateInput.addEventListener("change", syncPurchaseDatePlaceholder);

    calendarButton.addEventListener("click", () => {
      if (typeof purchaseDateInput.showPicker === "function") {
        purchaseDateInput.showPicker();
        return;
      }

      purchaseDateInput.focus();
      purchaseDateInput.click();
    });
  }

  const setMessage = (text, isError = false) => {
    message.textContent = text;
    message.classList.toggle(ERROR_CLASS_NAME, isError);
  };

  lookupButton.addEventListener("click", async () => {
    const isbn = fields.isbn.value.trim();
    if (!isbn) {
      setMessage(ISBN_REQUIRED_MESSAGE, true);
      return;
    }

    lookupButton.disabled = true;
    setMessage(LOOKUP_LOADING_MESSAGE);

    try {
      const params = new URLSearchParams({ [ISBN_QUERY_PARAM]: isbn });
      const response = await fetch(`${registerForm.dataset.isbnLookupUrl}?${params.toString()}`);
      const payload = await response.json();

      if (!response.ok) {
        setMessage(payload.error || LOOKUP_FAILED_MESSAGE, true);
        return;
      }

      Object.entries(payload.book).forEach(([key, value]) => {
        if (fields[key]) {
          fields[key].value = value ?? "";
        }
      });
      setMessage(LOOKUP_SUCCESS_MESSAGE);
    } catch (error) {
      setMessage(LOOKUP_FAILED_MESSAGE, true);
    } finally {
      lookupButton.disabled = false;
    }
  });
})();

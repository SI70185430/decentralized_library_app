(() => {
  const registerForm = document.getElementById("book-register-form");
  const lookupButton = document.getElementById("btn_book_info");
  const message = document.getElementById("book_lookup_message");

  const fields = {
    isbn: document.getElementById("input_isbn"),
    title: document.getElementById("input_title"),
    author: document.getElementById("input_author"),
    publisher: document.getElementById("input_publisher"),
    published_date: document.getElementById("input_publication_date"),
    cover_image_url: document.getElementById("input_image_url"),
    price: document.getElementById("input_price"),
    genre_code: document.getElementById("input_ccode"),
  };

  const purchaseDateField = document.querySelector("[data-date-placeholder-field]");
  if (purchaseDateField) {
    const purchaseDateInput = purchaseDateField.querySelector("input[type='date']");
    const calendarButton = document.getElementById("btn_calendar");
    const syncPurchaseDatePlaceholder = () => {
      purchaseDateField.classList.toggle("has-value", Boolean(purchaseDateInput.value));
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
    message.classList.toggle("book-register-error", isError);
  };

  lookupButton.addEventListener("click", async () => {
    const isbn = fields.isbn.value.trim();
    if (!isbn) {
      setMessage("ISBNコードを入力してください", true);
      return;
    }

    lookupButton.disabled = true;
    setMessage("書籍情報を取得しています...");

    try {
      const params = new URLSearchParams({ isbn });
      const response = await fetch(`${registerForm.dataset.isbnLookupUrl}?${params.toString()}`);
      const payload = await response.json();

      if (!response.ok) {
        setMessage(payload.error || "書籍情報を取得できませんでした", true);
        return;
      }

      Object.entries(payload.book).forEach(([key, value]) => {
        if (fields[key]) {
          fields[key].value = value ?? "";
        }
      });
      setMessage("書籍情報を反映しました");
    } catch (error) {
      setMessage("書籍情報を取得できませんでした", true);
    } finally {
      lookupButton.disabled = false;
    }
  });
})();

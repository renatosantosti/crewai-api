import pytest
from extract_numeric_values import extract_numeric_values

# Test header: Test extraction of a simple number.
# This test verifies that a numeric value expressed as digits is correctly extracted.
# Example text: "O número 123 está aqui."
# Expected value: 123.0 with type "NUMBER" and source "123"
def test_simple_number_extraction():
    text = "O número 123 está aqui."
    results = extract_numeric_values(text)
    expected = {
        "value": 123.0,
        "type": "NUMBER",
        "source": "123"
    }
    assert any(res["type"] == expected["type"] and 
               res["value"] == expected["value"] and 
               res["source"] == expected["source"] for res in results), "Simple number not extracted correctly."

# Test header: Test extraction of numeric measurement using digits.
# This test verifies extraction of a measurement expressed in digits.
# Example text: "Ele andou 25 metros."
# Expected value: 25.0 with unit "m", type "MEASURE" and source "25 metros"
def test_numeric_measurement_extraction():
    text = "Ele andou 25 metros."
    results = extract_numeric_values(text)
    expected = {
        "value": 25.0,
        "unit": "m",
        "type": "MEASURE",
        "source": "25 metros"
    }
    assert any(res.get("type") == expected["type"] and 
               res.get("value") == expected["value"] and 
               res.get("unit") == expected["unit"] and 
               res.get("source") == expected["source"] for res in results), "Numeric measurement not extracted properly."

# Test header: Test extraction of measurement using words.
# This test verifies extraction of a measurement when the number is expressed in words.
# Example text: "Ele correu dois km."
# Expected value: 2.0 with unit "km", type "MEASURE" and source "dois km"
def test_word_measurement_extraction():
    text = "Ele correu dois km."
    results = extract_numeric_values(text)
    expected = {
        "value": 2.0,
        "unit": "km",
        "type": "MEASURE",
        "source": "dois km"
    }
    
    assert any(res.get("type") == expected["type"] and
               res.get("value") == expected["value"] and 
               res.get("unit") == expected["unit"] and 
               expected["source"] in res.get("source").lower() for res in results), "Word-based measurement not handled correctly."

# Test header: Test extraction of BRL currency using digits.
# This test verifies extraction of a currency value in BRL expressed with symbols and digits.
# Example text: "Comprou por R$ 99,99 hoje."
# Expected value: 99.99 with unit "BRL", symbol "R$", type "MONEY" and source "R$ 99,99"
def test_currency_brl_numeric_extraction():
    text = "Comprou por R$ 99,99 hoje."
    results = extract_numeric_values(text)
    expected = {
        "value": 99.99,
        "unit": "BRL",
        "symbol": "R$",
        "type": "MONEY",
        "source": "R$ 99,99"
    }
    
    assert any(res.get("type") == expected["type"] and
               res.get("value") == expected["value"] and 
               res.get("unit") == expected["unit"] and 
               res.get("symbol") == expected["symbol"] and
               res.get("source").replace(" ", "") == expected["source"].replace(" ", "") for res in results), "BRL currency numeric extraction failed."

# Test header: Test extraction of USD currency using digits.
# This test verifies extraction of a currency value in USD expressed with the dollar symbol and digits.
# Example text: "Spent $10.50 on lunch." (text in English but specifically testing the case of dollars in Portuguese context "doláres" below)
# Expected value: 10.50 with unit "USD", symbol "$", type "MONEY" and source "$10.50"
def test_currency_usd_numeric_extraction():
    text = "Gastou $10.50 no almoço."
    results = extract_numeric_values(text)
    expected = {
        "value": 10.50,
        "unit": "USD",
        "symbol": "$",
        "type": "MONEY",
        "source": "$10.50"
    }
    
    assert any(res.get("type") == expected["type"] and
               res.get("value") == expected["value"] and
               res.get("unit") == expected["unit"] and
               res.get("symbol") == expected["symbol"] and
               res.get("source").replace(" ", "") == expected["source"] for res in results), "USD currency numeric extraction failed."

# Test header: Test extraction of BRL currency using words without centavos.
# This test verifies extraction when the currency value is expressed in words in Portuguese.
# Example text: "Ela pagou vinte e cinco reais pela entrada."
# Expected value: 25.0 with unit "BRL", symbol "R$", type "MONEY" and source containing "vinte e cinco reais"
def test_currency_words_extraction_without_centavos():
    text = "Ela pagou vinte e cinco reais pela entrada."
    results = extract_numeric_values(text)
    expected = {
        "value": 25.0,
        "unit": "BRL",
        "symbol": "R$",
        "type": "MONEY",
        "source": "vinte e cinco reais"
    }
    
    found = any(res.get("type") == expected["type"] and
                res.get("value") == expected["value"] and
                res.get("unit") == expected["unit"] and 
                res.get("symbol") == expected["symbol"] and
                expected["source"] in res.get("source").lower() 
               for res in results)
    assert found, "Currency words extraction without centavos failed."

# Test header: Test extraction of BRL currency using words with centavos.
# This test checks if the function correctly handles currency values expressed in words including centavos.
# Example text: "Ele pagou vinte e cinco reais e cinquenta centavos pelo ingresso."
# Expected value: 25.50 with unit "BRL", symbol "R$", type "MONEY" and source containing "vinte e cinco reais e cinquenta centavos"
def test_currency_words_extraction_with_centavos():
    text = "Ele pagou vinte e cinco reais e cinquenta centavos pelo ingresso."
    results = extract_numeric_values(text)
    expected = {
        "value": 25.50,
        "unit": "BRL",
        "symbol": "R$",
        "type": "MONEY",
        "source": "vinte e cinco reais e cinquenta centavos"
    }
    
    found = any(res.get("type") == expected["type"] and
                abs(res.get("value") - expected["value"]) < 0.001 and
                res.get("unit") == expected["unit"] and 
                res.get("symbol") == expected["symbol"] and
                expected["source"] in res.get("source").lower() 
               for res in results)
    assert found, "Currency words extraction with centavos failed."

# Test header: Test extraction of multiple monetary values expressed in words in the same sentence.
# This test verifies that multiple currency amounts in the same sentence are processed separately.
# Example text: "maria vendeu uma gata por vinte e tres reais e sophia comprou um cachorro por vinte e sete doláres"
# Expected values: One extraction with 23.0 BRL from "vinte e tres reais", and one extraction with 27.0 USD from "vinte e sete doláres"
def test_multiple_values_in_same_sentence():
    text = "maria vendeu uma gata por vinte e tres reais e sophia comprou um cachorro por vinte e sete doláres"
    results = extract_numeric_values(text)
    
    brl_found = any(res.get("type") == "MONEY" and res.get("unit") == "BRL" and 
                    "vinte e tres" in res.get("source").lower() for res in results)
    usd_found = any(res.get("type") == "MONEY" and res.get("unit") == "USD" and 
                    "vinte e sete" in res.get("source").lower() for res in results)
    
    assert brl_found and usd_found, "Multiple values extraction in the same sentence failed."

# Test header: Test extraction of measurements using words with complex text.
# This test verifies extraction of multiple measurement types expressed in words within a longer text.
# Example text: "Além disso, a distância foi de vinte e cinco km e a área mediu trezentos e cinco metros quadrados. Ela pesava quarenta e cinco gramas."
# Expected values: 25 km from "vinte e cinco km", 305 m from "trezentos e cinco" (meters) and 45 g from "quarenta e cinco gramas"
def test_measurement_with_complex_text():
    text = ("Além disso, a distância foi de vinte e cinco km e a área mediu trezentos e cinco metros quadrados. "
            "Ela pesava quarenta e cinco gramas.")
    results = extract_numeric_values(text)
    
    km_result = any(res.get("type") == "MEASURE" and res.get("unit") == "km" and 
                    "vinte e cinco" in res.get("source").lower() for res in results)
    m_result = any(res.get("type") == "MEASURE" and res.get("unit") == "m" and 
                   "trezentos e cinco" in res.get("source").lower() for res in results)
    g_result = any(res.get("type") == "MEASURE" and res.get("unit") == "g" and
                   "quarenta e cinco" in res.get("source").lower() for res in results)
                   
    assert km_result, "Measurement in km using words failed."
    assert m_result, "Measurement in meters using words failed."
    assert g_result, "Measurement in grams using words failed."


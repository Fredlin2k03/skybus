using System.Web;

namespace BusBooking.Api.Services;

public interface IUpiService
{
    /// <summary>Builds a standard "upi://pay" deep-link string that can be rendered as a QR code.</summary>
    string BuildUpiUri(string payeeVpa, string payeeName, decimal amount, string transactionNote, string transactionRef);
}

public class UpiService : IUpiService
{
    // NOTE: This is a MOCK generator for local development / demos only.
    // It produces a spec-shaped UPI deep link but does not integrate with any
    // real PSP/NPCI switch. In production this call would be replaced by a
    // real payment aggregator (Razorpay/PayU/Cashfree UPI Intent APIs) and
    // the resulting URI + webhook-driven status would come from that provider.
    public string BuildUpiUri(string payeeVpa, string payeeName, decimal amount, string transactionNote, string transactionRef)
    {
        var query = HttpUtility.ParseQueryString(string.Empty);
        query["pa"] = payeeVpa;                          // payee VPA
        query["pn"] = payeeName;                          // payee name
        query["am"] = amount.ToString("F2");               // amount
        query["cu"] = "INR";
        query["tn"] = transactionNote;                     // transaction note
        query["tr"] = transactionRef;                      // transaction reference id

        return $"upi://pay?{query}";
    }
}
